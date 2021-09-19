# Generated by Django 3.2.6 on 2021-09-19 02:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlossaryUploadFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.FileField(upload_to='glossary_files', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['txt'], message=['Please select a file having a ".txt" file extension.'])])),
                ('glossary_title', models.CharField(max_length=250)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Glossary file',
                'verbose_name_plural': 'Glossary files',
            },
        ),
        migrations.CreateModel(
            name='Glossary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='glossary_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='glossary_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'glossary',
                'verbose_name_plural': 'glossaries',
                'ordering': ['-title'],
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=250)),
                ('target', models.CharField(max_length=250)),
                ('resource', models.CharField(max_length=250)),
                ('notes', models.TextField(blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entry_created_by', to=settings.AUTH_USER_MODEL)),
                ('glossary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='resources.glossary')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entry_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'entry',
                'verbose_name_plural': 'entries',
            },
        ),
        migrations.AddIndex(
            model_name='glossary',
            index=models.Index(fields=['title'], name='resources_g_title_d378e8_idx'),
        ),
    ]
