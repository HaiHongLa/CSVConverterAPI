from django.urls import path
from converter import views


urlpatterns = [
    path("convert/<str:output_format>/", views.convert_csv, name="convert"),
    path("download/<str:filename>/", views.download_file, name="download"),
    path("clean-storage/", views.clean_storage, name="clean-storage"),
]