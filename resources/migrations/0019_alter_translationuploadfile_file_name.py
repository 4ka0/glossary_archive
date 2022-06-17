# Generated by Django 4.0.5 on 2022-06-17 07:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0018_translationuploadfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationuploadfile',
            name='file_name',
            field=models.FileField(upload_to='translation_files', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['tmx'], message=['Please select a file with a ".tmx" file extension.'])]),
        ),
    ]
