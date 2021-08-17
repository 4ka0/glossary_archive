from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Entry(models.Model):
    source = models.CharField(max_length=250)
    target = models.CharField(max_length=250)
    resource = models.CharField(max_length=250)
    notes = models.TextField(blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_by',
    )

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='updated_by',
    )

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        return f'{self.source} : {self.target}'

    def get_absolute_url(self):
        return reverse('entry_detail', args=[str(self.id)])


class CsvUploadFile(models.Model):

    file_name = models.FileField(
        upload_to="csv_files",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "csv",
                ],
                message=[
                    'Please select a file having a ".csv" file extension.'
                ],
            )
        ],
    )

    glossary_title = models.CharField(max_length=250)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CSV file"
        verbose_name_plural = "CSV files"

    def __str__(self):
        return str(self.file_name)

    # The default delete function is overidden to ensure that the associated
    # user-uploaded csv file is deleted as well as the object.
    def delete(self, *args, **kwargs):
        self.file_name.delete()
        super().delete(*args, **kwargs)
