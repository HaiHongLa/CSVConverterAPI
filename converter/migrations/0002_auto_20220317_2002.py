# Generated by Django 2.2.5 on 2022-03-18 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file_url',
            field=models.FileField(upload_to=''),
        ),
    ]
