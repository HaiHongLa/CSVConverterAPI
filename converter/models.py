from django.db import models

class File(models.Model):
    filename = models.CharField(max_length=500)
    file_url = models.FileField()
