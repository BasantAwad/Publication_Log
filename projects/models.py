# Import necessary Django modules for model definitions and validations
from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
# The Project model represents a research or work project.
class Project(models.Model):
    # Project title
    title = models.CharField(max_length=200)
    # Date the project was created
    created = models.DateField()
    # Team members involved in the project
    team = models.CharField(max_length=300)
    # Project abstract, defaulting to a placeholder if not provided
    abstract = models.TextField(default="No abstract yet")
    # Duration or timeframe of the project
    duration = models.CharField(max_length=100)
    # Domain or field of research/study
    domain = models.CharField(max_length=100)
    # Scientific case or justification for the project
    scientific_case = models.TextField()
    # Keywords for AI matching
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for AI matching")
    # Project status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Project leader/principal investigator
    principal_investigator = models.CharField(max_length=200, blank=True)
    # Funding information
    funding_source = models.CharField(max_length=200, blank=True)
    # Project website
    website = models.URLField(blank=True)
    # Created timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # Updated timestamp
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def get_keywords_list(self):
        """Get keywords as a list"""
        if self.keywords:
            return [keyword.strip() for keyword in self.keywords.split(',')]
        return []

    def get_publications_count(self):
        """Get total number of publications for this project"""
        return self.publications.count()

    # Returns the project title when the object is printed
    def __str__(self):
        return self.title

# The Author model represents an individual author.
class Author(models.Model):
    # Author's name must be unique; can be null or blank
    name = models.CharField(max_length=200, unique=True, null=True, blank=True)
    # Author's email address
    email = models.EmailField()
    # Author's profile picture
    profile_picture = models.ImageField(upload_to='author_pics/', blank=True, null=True)
    # Email preferences
    email_notifications = models.BooleanField(default=True)
    # Research interests for AI matching
    research_interests = models.TextField(blank=True, help_text="Comma-separated research interests")
    # Institution/affiliation
    institution = models.CharField(max_length=200, blank=True)
    # Department
    department = models.CharField(max_length=200, blank=True)
    # ORCID ID
    orcid_id = models.CharField(max_length=50, blank=True)
    # Created timestamp
    created_at = models.DateTimeField(default=timezone.now)
    # Updated timestamp
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def get_publications_count(self):
        """Get total number of publications by this author"""
        return self.primary_publications.count() + self.collaborated_publications.count()

    def get_research_interests_list(self):
        """Get research interests as a list"""
        if self.research_interests:
            return [interest.strip() for interest in self.research_interests.split(',')]
        return []

    # Returns the author's name when the object is printed
    def __str__(self):
        return self.name or f"Author {self.id}"

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
    # Primary author of the publication
    primary_author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='primary_publications',null=True, blank=True)
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
    collaborators = models.ManyToManyField(Author, related_name='collaborated_publications', blank=True)
    # Timestamp for when the publication was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Abstract text, with a default value
    abstract = models.TextField(default="No abstract yet")
    # Email notification status
    email_sent = models.BooleanField(default=False)
    # AI matching status
    ai_processed = models.BooleanField(default=False)
    # AI confidence score
    ai_confidence = models.FloatField(null=True, blank=True)

    # Custom validation: ensures either file or URL is provided for the publication
    def clean(self):
        if not self.file and not self.url:
            raise ValidationError("Either upload a file or provide a download link.")

    def get_all_authors(self):
        """Get all authors (primary + collaborators)"""
        authors = []
        if self.primary_author:
            authors.append(self.primary_author)
        authors.extend(self.collaborators.all())
        return authors
    
    def get_authors_display(self):
        """Get formatted string of all authors"""
        authors = self.get_all_authors()
        if not authors:
            return "No authors"
        elif len(authors) == 1:
            return authors[0].name
        elif len(authors) == 2:
            return f"{authors[0].name} and {authors[1].name}"
        else:
            author_names = [author.name for author in authors[:-1]]
            return f"{', '.join(author_names)}, and {authors[-1].name}"

    # Returns the publication title when the object is printed
    def __str__(self):
        if self.primary_author:
            return f"{self.title} by {self.primary_author.name}"
        elif self.collaborators.exists():
            return f"{self.title} by {', '.join([c.name for c in self.collaborators.all()])}"
        else:
            return f"{self.title} (no authors)"

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



AVATAR_CHOICES = [
    ("avatars/avatar1.png", "Avatar 1"),
    ("avatars/avatar2.png", "Avatar 2"),
    ("avatars/avatar3.png", "Avatar 3"),
    ("avatars/avatar4.png", "Avatar 4"),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    selected_avatar = models.CharField(max_length=100, choices=AVATAR_CHOICES, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        elif self.selected_avatar:
            return f'/static/{self.selected_avatar}'
        return '/static/avatars/default.png'


class MessageRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)
    initial_message = models.TextField(blank=True, help_text="Initial message with the request")
    
    class Meta:
        unique_together = ['sender', 'recipient']
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username} ({self.status})"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    content = models.TextField( null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    request = models.ForeignKey(MessageRequest, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.content[:50]}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message_request', 'Message Request'),
        ('message_received', 'Message Received'),
        ('message_read', 'Message Read'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    message_request = models.ForeignKey(MessageRequest, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}: {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()

# ========================
# GROUP MESSAGING MODELS
# ========================

class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Group: {self.name}"
    
    def get_members_count(self):
        return self.members.count()
    
    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

class GroupMessage(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages_sent')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read_by = models.ManyToManyField(User, related_name='read_group_messages', blank=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}"
    
    def mark_as_read_by(self, user):
        self.is_read_by.add(user)
    
    def get_read_count(self):
        return self.is_read_by.count()

class GroupInvitation(models.Model):
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_group_invitations')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['group', 'invitee']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.invitee.username} for {self.group.name}"