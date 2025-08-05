from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    created = models.DateField()
    collaborators  = models.CharField(max_length=300)
    abstract  = models.TextField()
    duration = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    scientific_case = models.TextField()

    def __str__(self):
        return self.title

from django.db import models

PUBLICATION_TYPES = [
    ('Journal', 'Journal'),
    ('Conference', 'Conference'),
    ('Workshop', 'Workshop'),
    ('Other', 'Other'),
]

class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Publication(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to='publications/files/', blank=True)
    image = models.ImageField(upload_to='publications/images/', blank=True)
    type = models.CharField(max_length=100, choices=PUBLICATION_TYPES)

    authors = models.ManyToManyField(Author)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

class HarvestMatchCandidate(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    matched_by_ai = models.BooleanField(default=True)
    confirmed_by_admin = models.BooleanField(null=True, blank=True)  # True/False/None
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Match: {self.publication.title} ↔ {self.project.title}"

