# Generated by Django 3.2.11 on 2022-01-16 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0006_alter_glossary_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glossary',
            name='title',
            field=models.CharField(max_length=60),
        ),
    ]
