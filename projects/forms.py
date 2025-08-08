import os
from urllib.parse import urlparse
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import requests
from .models import Author, Publication
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PublicationForm(forms.ModelForm):
    new_collaborators = forms.CharField(
        required=False,
        label="Authors",
        help_text="Enter comma-separated author names."
    )
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project  # Store the project for later use if needed

    class Meta:
        model = Publication
        fields = ['title', 'abstract', 'file', 'url' , 'year']  # Ensure these fields exist in your model

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')  # Match the field name in your model
        url = cleaned_data.get('url')     # Match the field name in your model

        if not file and not url:
            raise forms.ValidationError("Please upload a file or provide a download link.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            self.save_m2m()

            # Parse authors
            author_names = self.cleaned_data.get("new_collaborators", "")
            author_names = [name.strip() for name in author_names.split(",") if name.strip()]
            authors = []

            for name in author_names:
                author, _ = Author.objects.get_or_create(name=name)
                authors.append(author)

            instance.collaborators.set(authors)  # Ensure 'collaborators' is a ManyToManyField

        return instance




    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserCreation(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")





def fetch_and_save_file_from_url(publication_instance, url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        parsed_url = urlparse(url)
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



