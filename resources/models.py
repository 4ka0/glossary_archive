from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Glossary(models.Model):
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
        # indexes & ordering used to order glossary objects alphabetically
        indexes = [models.Index(fields=['title'])]
        ordering = ['title']
        verbose_name = 'glossary'
        verbose_name_plural = 'glossaries'

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

    glossary_name = models.CharField(max_length=70)
    glossary_notes = models.CharField(max_length=70)  # Change to textfield ???
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


class Client(models.Model):
    '''
    Model for translation clients.
    Used as a field in the Translation model.
    '''
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'client'
        verbose_name_plural = 'clients'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('client_detail', args=[str(self.id)])


class Field(models.Model):
    '''
    Model for translation fields as in 分野.
    Used as a field in the Translation model.
    '''
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'field'
        verbose_name_plural = 'fields'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('field_detail', args=[str(self.id)])


class Translation(models.Model):
    '''
    Model for for an actual translation job.
    '''
    job_number = models.CharField(max_length=255)
    field = models.ForeignKey(
        Field,
        related_name="fields",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='uploaded_translations',
        null=True,
        on_delete=models.SET_NULL,
    )
    client = models.ForeignKey(
        Client,
        related_name="clients",
        on_delete=models.CASCADE,
        null=True,
        blank=True
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

    def get_absolute_url(self):
        return reverse('segment_detail', args=[str(self.id)])
