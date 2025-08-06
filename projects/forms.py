import os
import requests
from django import forms
from .models import Publication, Author
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

class PublicationForm(forms.ModelForm):
    new_collaborators = forms.CharField(
        required=False,
        label="Authors",
        help_text="Enter comma-separated author names."
    )

    class Meta:
        model = Publication
        fields = ['title', 'abstract', 'file', 'url'] 
            
    def clean(self):
        cleaned_data = super().clean()
        pdf_file = cleaned_data.get('pdf_file')
        download_link = cleaned_data.get('download_link')

        if not pdf_file and not download_link:
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

            instance.collaborators.set(authors)

        return instance



    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']





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



