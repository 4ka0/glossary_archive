# Generated by Django 3.2.6 on 2021-08-10 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_csvuploadfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvuploadfile',
            name='glossary_title',
            field=models.CharField(default='', max_length=250),
            preserve_default=False,
        ),
    ]
