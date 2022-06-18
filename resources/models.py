from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Glossary(models.Model):
    glossary_file = models.FileField(
        null=True,
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
    title = models.CharField(max_length=70)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_glossaries',
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updated_glossaries',
        null=True,
        on_delete=models.SET_NULL,
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'glossary'
        verbose_name_plural = 'glossaries'
        # indexes & ordering used to order glossary objects alphabetically
        indexes = [models.Index(fields=['title'])]
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glossary_detail', args=[str(self.id)])


class Entry(models.Model):
    glossary = models.ForeignKey(
        Glossary,
        related_name="entries",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    source = models.CharField(max_length=250)
    target = models.CharField(max_length=250)
    notes = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_entries',
        null=True,
        on_delete=models.SET_NULL,
    )
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updated_entries',
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'entry'
        verbose_name_plural = 'entries'

    def __str__(self):
        return f'{self.source} : {self.target}'

    def get_absolute_url(self):
        return reverse('entry_detail', args=[str(self.id)])


class Translation(models.Model):
    translation_file = models.FileField(
        null=True,
        upload_to="translation_files",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "tmx",
                ],
                message=[
                    'Please select a file with a ".tmx" file extension.'
                ],
            )
        ],
    )
    job_number = models.CharField(max_length=255)
    field = models.CharField(max_length=255, blank=True)
    client = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='uploaded_translations',
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'translation'
        verbose_name_plural = 'translations'

    def __str__(self):
        return self.job_number

    def get_absolute_url(self):
        return reverse('translation_detail', args=[str(self.id)])


class Segment(models.Model):
    '''
    Model for a translation segment, i.e. a pair of source and target strings.
    Child model of the Translation model.
    '''
    translation = models.ForeignKey(
        Translation,
        related_name="segments",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    source = models.TextField()
    target = models.TextField()

    class Meta:
        verbose_name = 'segment'
        verbose_name_plural = 'segments'

    def __str__(self):
        return f'{self.source} : {self.target}'
