# Generated by Django 4.0.5 on 2022-06-10 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0013_alter_glossary_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='glossaryuploadfile',
            name='glossary_notes',
            field=models.CharField(default='', max_length=70),
            preserve_default=False,
        ),
    ]
