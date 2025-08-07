from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth.models import User


class Project(models.Model):
    title = models.CharField(max_length=200)
    created= models.DateField()
    team  = models.CharField(max_length=300)
    abstract = models.TextField(default="No abstract yet")
    duration = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    scientific_case = models.TextField()

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=200)
    email=models.EmailField()

    def __str__(self):
        return self.name


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

class Publication(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=200)
    author = models.CharField(Author,max_length=200)
    url = models.URLField(blank=True)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to='publications/files/', blank=True)
    image = models.ImageField(upload_to='publications/images/', blank=True)
    type = models.CharField(max_length=100, choices=PUBLICATION_TYPES)
    collaborators = models.ManyToManyField(Author)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    abstract = models.TextField(default="No abstract yet")


    def clean(self):
        if not self.pdf_file and not self.download_link:
            raise ValidationError("Either upload a file or provide a download link.")

    def __str__(self):
        return self.title

class HarvestMatchCandidate(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    matched_by_ai = models.BooleanField(default=True)
    confirmed_by_admin = models.BooleanField(null=True, blank=True) 
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Match: {self.publication.title} ↔ {self.project.title}"

def get_default_project():
    try:
        return Project.objects.first().id
    except:
        return None

class MatchRequest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=get_default_project)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    match_title = models.CharField(max_length=255)
    match_score = models.FloatField()
    match_authors = models.TextField()
    approved = models.BooleanField(null=True)

    def __str__(self):
        return f"MatchRequest({self.project.title} ← {self.publication.title})"


class UploadToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"

