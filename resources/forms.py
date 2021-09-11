# from resources.views import glossary_upload
from django import forms

from .models import GlossaryUploadFile


class GlossaryUploadForm(forms.ModelForm):
    file_name = forms.FileField(
        label="Filename",
        error_messages={
            "empty": "The selected file is empty.",
            "required": "Please select a text file (.txt).",
            "missing": "A file has not been provided.",
            "invalid": "The file format is not correct. Please select a text file (.txt).",
        },
    )

    class Meta:
        model = GlossaryUploadFile
        fields = ("file_name", "glossary_title")
