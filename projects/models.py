from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    created = models.DateField()
    collaborators  = models.CharField(max_length=300)
    abstract = models.TextField(default="No abstract yet")
    duration = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    scientific_case = models.TextField()

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


PUBLICATION_TYPES = [
    ('Journal', 'Journal'),
    ('Conference', 'Conference'),
    ('Workshop', 'Workshop'),
    ('Other', 'Other'),
]

class Publication(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to='publications/files/', blank=True)
    image = models.ImageField(upload_to='publications/images/', blank=True)
    type = models.CharField(max_length=100, choices=PUBLICATION_TYPES)
    collaborators = models.ManyToManyField(Author)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    abstract = models.TextField(default="No abstract yet")



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

class MatchRequest(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    match_title = models.CharField(max_length=255)
    match_authors = models.TextField()
    match_abstract = models.TextField(blank=True, null=True)
    match_score = models.FloatField()
    approved = models.BooleanField(null=True, blank=True)  # None = not reviewed yet
    created_at = models.DateTimeField(auto_now_add=True)

    def is_reviewed(self):
        return self.approved is not None

    def __str__(self):
        return f"Match for '{self.publication.title}' | Approved: {self.approved}"



