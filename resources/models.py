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


class GlossaryUploadFile(models.Model):

    file_name = models.FileField(
        upload_to="glossary_files",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "txt",
                ],
                message=[
                    'Please select a file having a ".txt" file extension.'
                ],
            )
        ],
    )

    glossary_title = models.CharField(max_length=250)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Glossary file"
        verbose_name_plural = "Glossary files"

    def __str__(self):
        return str(self.file_name)

    # The default delete function is overidden to ensure that the associated
    # user-uploaded text file is deleted as well as the object.
    def delete(self, *args, **kwargs):
        self.file_name.delete()
        super().delete(*args, **kwargs)
