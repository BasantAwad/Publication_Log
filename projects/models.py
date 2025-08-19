# Import necessary Django modules for model definitions and validations
from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth.models import User

# The Project model represents a research or work project.
class Project(models.Model):
    # Project title
    title = models.CharField(max_length=200)
    # Date the project was created
    created= models.DateField()
    # Team members involved in the project
    team  = models.CharField(max_length=300)
    # Project abstract, defaulting to a placeholder if not provided
    abstract = models.TextField(default="No abstract yet")
    # Duration or timeframe of the project
    duration = models.CharField(max_length=100)
    # Domain or field of research/study
    domain = models.CharField(max_length=100)
    # Scientific case or justification for the project
    scientific_case = models.TextField()

    # Returns the project title when the object is printed
    def __str__(self):
        return self.title

# The Author model represents an individual author.
class Author(models.Model):
    # Author's name must be unique; can be null or blank
    name = models.CharField(max_length=200, unique=True,null=True, blank=True)
    # Author's email address
    email=models.EmailField()

    # Returns the author's name when the object is printed
    def __str__(self):
        return self.name

# List of publication types as choices for the Publication model
PUBLICATION_TYPES = [
    ('Journal', 'Journal Article'),  
    ('Conference', 'Conference Paper'),  
    ('Workshop', 'Workshop Paper'),  
    ('Preprint', 'Preprint'),  
    ('Thesis', 'Thesis/Dissertation'),  
    ('Book', 'Book'),  
    ('Book Chapter', 'Book Chapter'),  
    ('Technical Report', 'Technical Report'),  
    ('Patent', 'Patent'),  
    ('Poster', 'Poster'),  
    ('Abstract', 'Abstract'),  
    ('Editorial', 'Editorial'),  
    ('Review', 'Review Article'),  
    ('Magazine', 'Magazine Article'),  
    ('Blog', 'Blog Post'),  
    ('White Paper', 'White Paper'),  
    ('Dataset', 'Dataset'),  
    ('Software', 'Software/Code'),  
    ('Standard', 'Standard/Specification'),  
    ('Symposium', 'Symposium'),  
    ('Tutorial', 'Tutorial'),  
    ('Keynote', 'Keynote Speech'),  
    ('Invited Talk', 'Invited Talk'),  
    ('Panel', 'Panel Discussion'),  
    ('Exhibition', 'Exhibition'),  
    ('Other', 'Other'),  
]

# The Publication model represents a published work associated with a project.
class Publication(models.Model):
    # Link to the associated project (many publications can belong to one project)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='publications')
    # Title of the publication
    title = models.CharField(max_length=200)
    # Author field, intended to reference Author model, but incorrectly defined (should be ForeignKey or ManyToMany)
    author = models.CharField(Author,max_length=200)
    # URL to the publication (optional)
    url = models.URLField(blank=True)
    # Year of publication
    year = models.PositiveIntegerField()
    # Optional file upload for the publication (e.g., PDF)
    file = models.FileField(upload_to='publications/files/', blank=True)
    # Optional image related to the publication
    image = models.ImageField(upload_to='publications/images/', blank=True)
    # Publication type (from the choices defined above)
    type = models.CharField(max_length=100, choices=PUBLICATION_TYPES)
    # Collaborators, can be multiple authors
    collaborators = models.ManyToManyField(Author)
    # Timestamp for when the publication was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Abstract text, with a default value
    abstract = models.TextField(default="No abstract yet")

    # Custom validation: ensures either file or URL is provided for the publication
    def clean(self):
        if not self.file and not self.url:
            raise ValidationError("Either upload a file or provide a download link.")

    # Returns the publication title when the object is printed
    def __str__(self):
        return self.title

# HarvestMatchCandidate model represents a possible match between a publication and a project, suggested by AI.
class HarvestMatchCandidate(models.Model):
    # Link to the matched publication
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    # Link to the matched project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # Whether the match was suggested by AI
    matched_by_ai = models.BooleanField(default=True)
    # Whether the match has been confirmed by an admin (nullable)
    confirmed_by_admin = models.BooleanField(null=True, blank=True) 
    # Confidence score for the match (nullable)
    confidence_score = models.FloatField(null=True, blank=True)
    # Timestamp for when the candidate was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Returns a string describing the match
    def __str__(self):
        return f"AI Match: {self.publication.title} ↔ {self.project.title}"

# Helper function for default project selection (used in MatchRequest model)
def get_default_project():
    try:
        # Returns the ID of the first Project object
        return Project.objects.first().id
    except:
        # Returns None if no Project exists
        return None

# MatchRequest model represents a user-initiated request to match a publication to a project.
class MatchRequest(models.Model):
    # Associated project, defaulting to first project if possible
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=get_default_project)
    # Associated publication
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    # Title of the match request
    match_title = models.CharField(max_length=255)
    # Score indicating the strength of the match
    match_score = models.FloatField()
    # Authors involved in the match (stored as text)
    match_authors = models.TextField()
    # Approval status (nullable)
    approved = models.BooleanField(null=True)

    # Returns a string describing the match request
    def __str__(self):
        return f"MatchRequest({self.project.title} ← {self.publication.title})"

# UploadToken model is used for secure upload actions, e.g., file uploads.
class UploadToken(models.Model):
    # Unique token for upload, using UUID
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # User who owns the token
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Whether the token has been used
    is_used = models.BooleanField(default=False)
    # Timestamp for when the token was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Returns a string describing the token and user
    def __str__(self):
        return f"Token for {self.user.username}"
