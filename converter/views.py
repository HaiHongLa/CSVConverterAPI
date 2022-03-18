from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import pandas as pd
import os
from datetime import datetime
import re
from django.conf import settings
from rest_framework import status, serializers
import mimetypes
from converter.models import File

from datetime import timedelta
from pathlib import Path


def should_delete(filename):
    path = Path(filename).stem
    dt_str = path[-20:-10]
    target_dt = datetime.datetime.today() - timedelta(hours = 2) # check for all files created 2 hours ago
    dt = datetime.datetime(int(dt_str[:4]), int(dt_str[4:6]), int(dt_str[6:8]), int(dt_str[8:]))
    return dt < target_dt

import boto3
import io

@api_view(['GET',])
def test_storage(request):
    # path = open(os.path.join(settings.BASE_DIR, 'media', "baseball_allstar.csv"))
    # new_file = File(filename="baseball_allstar.csv", file_url=path)
    # new_file.save()
    df = pd.read_csv("media/baseball_allstar.csv")
    # print(settings.AWS_STORAGE_BUCKET_NAME)
    # df.to_csv("s3://{}/baseball_allstar_saved12313213.csv".format(settings.AWS_STORAGE_BUCKET_NAME), storage_options={
    #     "key": settings.AWS_ACCESS_KEY_ID,
    #     "secret": settings.AWS_SECRET_ACCESS_KEY,
    #     "anon": False,
    #     "token": ""
    # })

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    with io.StringIO() as csv_buffer:
        print(type(csv_buffer.getvalue()))
        df.to_excel("media/baseball_allstar.xlsx")

        response = s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key="baseball_allstars_saved.xlsx", Body=open("media/baseball_allstar.xlsx", "rb")
        )

        os.remove("media/baseball_allstar.xlsx")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")

    # s3 = s3fs.S3FileSystem(anon=True)

    # # Use 'w' for py3, 'wb' for py2
    # with s3.open('{}/baseball_allstar_saveed.csv'.format(settings.AWS_STORAGE_BUCKET_NAME),'w') as f:
    #     df.to_csv(f, storage_options={
    #     "key": settings.AWS_ACCESS_KEY_ID,
    #     "secret": settings.AWS_SECRET_ACCESS_KEY
    # })

    return JsonResponse({"msg": "saving done"})

@api_view(['POST',])
def clean_storage(request):
    files = os.listdir("./media") # find all files in the media folder
    if len(files) == 0: return JsonResponse({"msg": "Storage is clear"}, status=status.HTTP_200_OK)

    deleted_files = list() # store the results
    try:
        for path in files:
            if should_delete(path):
                deleted_files.append(path)
                os.remove(os.path.join("media", path))
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return JsonResponse({"msg": "Deleting done", "deleted_files": deleted_files}, status=status.HTTP_200_OK)

@api_view(['GET',])
def download_file(request, filename):
    filepath = os.path.join(settings.BASE_DIR, "media", filename)
    path = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type = mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

@api_view(["POST",])
def convert_csv(request, output_format):

    allowed_outputs = {"html", "xlsx", "json", "xml", "pkl", "txt"}

    if output_format not in allowed_outputs:
        return JsonResponse({"msg": "Output format not allowed"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    try:
        f = request.FILES.dict()["file"]
        try:
            data = pd.read_csv(f)
        except:
            raise ValueError("An error occurred when reading file, please make sure csv file only contains tabular data")

        # for html output
        if output_format == "html":
            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".html"
            filepath = os.path.join("media/", filename)
            data.to_html(filepath)

        # output to excel file
        elif output_format == "xlsx":
            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".xlsx"
            filepath = os.path.join("media/", filename)
            print(filepath)
            data.to_excel(filepath)

        # output to json file
        elif output_format == "json":
            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".json"
            filepath = os.path.join("media/", filename)
            data.to_json(filepath)

        # output to text file
        elif output_format == "txt":
            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".txt"
            filepath = os.path.join("media/", filename)
            data.to_csv(filepath)

        # output to pickle file
        elif output_format == "pkl":
            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".pkl"
            filepath = os.path.join("media/", filename)
            data.to_pickle(filepath)

        # output to xml file
        elif output_format == "xml":
            # check if column name starts with a number
            for column_name in data.columns:
                if column_name[0].isdigit():
                    # data.rename(columns = {column_name: "".join(re.findall('^[a-zA-Z0-9_]+$', ('_' + column_name).replace(" ", "_") ) ) }, inplace = True)
                    data.rename(columns = {str(column_name): "_" + column_name})

            # clean column names
            for column_name in data.columns:
                data.rename(columns = {str(column_name) : str(re.sub('[^A-Za-z0-9_ ]+', '', str(column_name))).replace(" ", "_")}, inplace = True)

            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".xml"
            filepath = os.path.join("media/", filename)
            
            data.to_xml(filepath)

        response = s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=filename, Body=open(filepath, "rb")
        )

        try:
            os.remove(filepath)
        except:
            pass

        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            raise ValueError("An error occured storing your file")


        return JsonResponse({"msg": "Convert done", "filename": filename}, status=status.HTTP_200_OK)

    except ValueError as val_err:
        return JsonResponse({"msg": str(val_err) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        print(e)
        return JsonResponse({"msg": "An error occured while converting file" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"msg": "Converting unsuccessful"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)