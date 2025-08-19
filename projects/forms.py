import os
from urllib.parse import urlparse
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import requests
from .models import Author, Publication
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Form for creating or editing a Publication instance
class PublicationForm(forms.ModelForm):
    # Additional field to capture new collaborators (authors) as a comma-separated string
    new_collaborators = forms.CharField(
        required=False,
        label="Authors",
        help_text="Enter comma-separated author names."
    )
    
    def __init__(self, *args, project=None, **kwargs):
        # Custom constructor to optionally accept a project
        super().__init__(*args, **kwargs)
        self.project = project  # Store the project for later use if needed

    class Meta:
        # Specify the model this form is tied to
        model = Publication
        # List the fields to be included in the form
        fields = ['title', 'abstract', 'file', 'url' , 'year']

    def clean(self):
        # Custom validation logic for the form
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        # Ensure at least one of file or url is provided
        if not file and not url:
            raise forms.ValidationError("Please upload a file or provide a download link.")
        return cleaned_data

    def save(self, commit=True):
        # Custom save logic to also handle collaborators
        instance = super().save(commit=False)
        
        if commit:
            instance.save()  # Save the publication instance
            self.save_m2m()  # Save many-to-many relationships

            # Parse authors from the new_collaborators field
            author_names = self.cleaned_data.get("new_collaborators", "")
            author_names = [name.strip() for name in author_names.split(",") if name.strip()]
            authors = []

            for name in author_names:
                # Get or create each author by name
                author, _ = Author.objects.get_or_create(name=name)
                authors.append(author)

            # Set the collaborators field (ManyToMany relationship)
            instance.collaborators.set(authors)

        return instance


# Form for updating an existing User's basic profile information
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# Form for creating a new User, extending Django's built-in UserCreationForm
class UserCreation(UserCreationForm):
    # Require email during registration
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def clean_email(self):
        # Custom validation to ensure email uniqueness
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

# Utility function to fetch a file from a URL and save it to a Publication instance
def fetch_and_save_file_from_url(publication_instance, url):
    try:
        response = requests.get(url, timeout=15)  # Download file from URL
        response.raise_for_status()
        
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        # Ensure the file is of an allowed type (.pdf, .doc, .docx)
        if not filename.endswith(('.pdf', '.docx', '.doc')):
            raise ValidationError("URL must point to a .pdf or .doc/.docx file")

        # Save the downloaded file to the publication's file field
        publication_instance.file.save(
            filename,
            ContentFile(response.content),
            save=True
        )
        return True  # Valid URL and saved
    except Exception as e:
        print(f"Download failed: {e}")
        return False  # If download fails or invalid
