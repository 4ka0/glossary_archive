from django import forms

from .models import Entry, Glossary, GlossaryUploadFile


class CreateGlossaryForm(forms.ModelForm):
    pass


class CreateEntryForm(forms.ModelForm):
    glossary = forms.ModelChoiceField(
        label='Add to an existing glossary?',
        queryset=Glossary.objects.all(),
        required=False
    )
    new_glossary = forms.CharField(
        label='Or create a new glossary for this term?',
        widget=forms.TextInput(attrs={'placeholder': 'Enter the name for the new glossary'}),
        required=False
    )
    source = forms.CharField(label='Source language term')
    target = forms.CharField(label='Target language term')
    notes = forms.CharField(
        label='Notes (optional)',
        widget=forms.Textarea(attrs={'rows': 6}),
        required=False
    )

    class Meta:
        model = Entry
        fields = ('source', 'target', 'glossary', 'notes')

    def clean(self):
        '''
        Overwritten to handle validation for both glossary fields.
        Only one of the glossary fields should be filled in.
        Also handles the case where a new glossary is to be created for the new term.
        '''
        cleaned_data = super().clean()
        existing_glossary = cleaned_data.get('glossary')
        new_glossary = cleaned_data.get('new_glossary')

        # If both fields have been entered, output error
        if existing_glossary and new_glossary:
            existing_glossary_msg = "Please select an existing glossary ..."
            new_glossary_msg = "... or create a new glossary, not both."
            self.add_error('glossary', existing_glossary_msg)
            self.add_error('new_glossary', new_glossary_msg)

        # If neither of the fields have been entered, output error
        if not (existing_glossary or new_glossary):
            existing_glossary_msg = "Please select an existing glossary ..."
            new_glossary_msg = "... or create a new glossary."
            self.add_error('glossary', existing_glossary_msg)
            self.add_error('new_glossary', new_glossary_msg)

        # If new term is to be added to a new glossary
        if not existing_glossary and new_glossary:
            # If input title for new glossary already exists, output error
            if Glossary.objects.filter(title__iexact=new_glossary).exists():
                msg = 'A glossary with that title already exists.'
                self.add_error('new_glossary', msg)
            else:
                # Create new Glossary instance having title from new_glossary
                create_glossary = Glossary(title=new_glossary)
                create_glossary.save()
                # Add new glossary object to form data (immutable so have to use copy() here)
                cleaned_data = self.data.copy()
                cleaned_data['glossary'] = create_glossary
                return cleaned_data


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
