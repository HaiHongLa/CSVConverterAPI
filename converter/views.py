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

    try:
        f = request.FILES.dict()["file"]
        try:
            data = pd.read_csv(f)
        except:
            raise Exception("Unable to convert file")

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
                    data.rename(columns = {column_name: "".join(re.findall('[0-9A-Za-z\'_.]+', ('_' + column_name).replace(" ", "_") ) ) }, inplace = True)

            filename = f.name[:-4] + "_" + "".join(re.findall('[0-9]+', str(datetime.now()))) + ".xml"
            filepath = os.path.join("media/", filename)
            
            data.to_xml(filepath)

        return JsonResponse({"msg": "Convert done", "filename": filename}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return JsonResponse({"msg": str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({"msg": "Converting unsuccessful"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)