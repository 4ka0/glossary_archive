# from resources.views import glossary_upload
from django import forms

from .models import CsvUploadFile


class CsvUploadForm(forms.ModelForm):
    file_name = forms.FileField(
        label="Filename",
        error_messages={
            "empty": "The selected file is empty.",
            "required": "Please select a CSV file.",
            "missing": "A file has not been provided.",
            "invalid": "The file format is not correct. Please select a CSV file.",
        },
    )

    class Meta:
        model = CsvUploadFile
        fields = ("file_name", "glossary_title")
