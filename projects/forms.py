import os
import requests
from cProfile import label
from email.policy import default
from django import forms
from .models import Publication, Author
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

class PublicationForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Authors",
    )

    class Meta:
        model = Publication
        exclude = ['project']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if project:
            team_names = [name.strip() for name in project.collaborators.split(',')]
            authors = [Author.objects.get_or_create(name=name)[0] for name in team_names]
            self.fields['authors'].queryset = Author.objects.filter(id__in=[a.id for a in authors])

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


    

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UploadPublicationForm(forms.ModelForm):
    author_name = forms.CharField(
        max_length=100,
        required=True,
        label="Author Name",
        help_text="Enter your full name."
    )

    collaborators = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Collaborators"
    )

    file = forms.FileField(
        required=False,
        label="Upload Publication File (.pdf or .docx)",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'})
    )

    download_link = forms.URLField(
        required=False,
        label="Downloadable Link (must be direct download)",
        help_text="Example: a Google Drive direct download link or Dropbox direct link"
    )

    class Meta:
        model = Publication
        fields = ['title', 'abstract', 'collaborators', 'file', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_validation_failed = False

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        download_link = cleaned_data.get('download_link')

        if not file and not download_link:
            raise forms.ValidationError("You must upload a file or provide a downloadable link.")

    
        if download_link:
            if not any(keyword in download_link.lower() for keyword in ['download', 'dl', 'export=download']):
                self.add_error('download_link', "Make sure this is a direct downloadable link.")
                self.url_validation_failed = True
            else:
                self.url_validation_failed = False

        return cleaned_data


def fetch_and_save_file_from_url(publication_instance, download_url):
    try:
        response = requests.get(download_url, timeout=15)
        response.raise_for_status()
        
        parsed_url = urlparse(download_url)
        filename = os.path.basename(parsed_url.path)
        if not filename.endswith(('.pdf', '.docx', '.doc')):
            raise ValidationError("URL must point to a .pdf or .doc/.docx file")

        publication_instance.file.save(
            filename,
            ContentFile(response.content),
            save=True
        )
        return True  # Valid URL and saved
    except Exception as e:
        print(f"Download failed: {e}")
        return False  # For url_validation = False



