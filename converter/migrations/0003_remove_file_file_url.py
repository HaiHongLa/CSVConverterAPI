# Generated by Django 2.2.5 on 2022-03-18 03:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0002_auto_20220317_2002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='file_url',
        ),
    ]