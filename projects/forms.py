import os
from urllib.parse import urlparse
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import requests
from .models import Author, Publication , MessageRequest , Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Form for creating or editing a Publication instance
class PublicationForm(forms.ModelForm):
    # Primary author field
    primary_author_name = forms.CharField(
        required=True,
        label="Primary Author",
        help_text="Enter the primary author's name."
    )
    primary_author_email = forms.EmailField(
        required=True,
        label="Primary Author Email",
        help_text="Enter the primary author's email address."
    )
    # Additional field to capture new collaborators (authors) as a comma-separated string
    new_collaborators = forms.CharField(
        required=False,
        label="Additional Authors",
        help_text="Enter comma-separated additional author names (optional)."
    )
    
    def __init__(self, *args, project=None, **kwargs):
        # Custom constructor to optionally accept a project
        super().__init__(*args, **kwargs)
        self.project = project  # Store the project for later use if needed

    class Meta:
        # Specify the model this form is tied to
        model = Publication
        # List the fields to be included in the form
        fields = ['title', 'abstract', 'file', 'url', 'year', 'type']

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
        # Custom save logic to also handle authors
        instance = super().save(commit=False)
        
        if commit:
            # Handle primary author
            primary_author_name = self.cleaned_data.get("primary_author_name", "")
            primary_author_email = self.cleaned_data.get("primary_author_email", "")
            
            if primary_author_name and primary_author_email:
                primary_author, _ = Author.objects.get_or_create(
                    name=primary_author_name,
                    defaults={'email': primary_author_email}
                )
                instance.primary_author = primary_author
            
            instance.save()  # Save the publication instance
            self.save_m2m()  # Save many-to-many relationships

            # Parse additional authors from the new_collaborators field
            author_names = self.cleaned_data.get("new_collaborators", "")
            if author_names:
                author_names = [name.strip() for name in author_names.split(",") if name.strip()]
                authors = []

                for name in author_names:
                    # Get or create each author by name (with default email)
                    author, _ = Author.objects.get_or_create(
                        name=name,
                        defaults={'email': f"{name.lower().replace(' ', '.')}@example.com"}
                    )
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


class MessageRequestForm(forms.ModelForm):
    class Meta:
        model = MessageRequest
        fields = []

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']