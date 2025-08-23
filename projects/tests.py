# tests.py — Publication Log (Django)
# How to run: python manage.py test -v 2 -s
# The -s flag ensures print statements are shown.

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date
import tempfile
import os

from .models import Project, Publication, Author, UserProfile, MessageRequest, Message, Notification

# ---------------------------
# Test Configuration
# ---------------------------

class TestConfig:
    """Configuration for test data and URLs"""
    
    # Test user credentials
    TEST_USERNAME = "testuser"
    TEST_PASSWORD = "TestPass123!"
    TEST_EMAIL = "test@example.com"
    
    # Counter for unique usernames
    _username_counter = 0
    
    @classmethod
    def get_unique_username(cls):
        """Generate a unique username for tests"""
        cls._username_counter += 1
        return f"testuser_{cls._username_counter}"
    
    # Test project data
    TEST_PROJECT_DATA = {
        'title': 'Test Research Project',
        'created': date(2024, 1, 15),
        'team': 'Test Team Members',
        'abstract': 'This is a test project abstract for testing purposes.',
        'duration': '6 months',
        'domain': 'Computer Science',
        'scientific_case': 'This project aims to test the publication system.'
    }
    
    # Test publication data
    TEST_PUBLICATION_DATA = {
        'title': 'Test Publication Title',
        'year': 2024,
        'type': 'Journal',
        'abstract': 'This is a test publication abstract.',
        'url': 'https://example.com/test-paper.pdf'
    }
    
    # Test author data
    TEST_AUTHOR_DATA = {
        'name': 'Test Author',
        'email': 'author@example.com'
    }

# ---------------------------
# Test Utilities
# ---------------------------

def create_test_user(username=None, password=None, email=None, is_staff=False):
    """Create a test user with optional parameters"""
    username = username or TestConfig.get_unique_username()
    password = password or TestConfig.TEST_PASSWORD
    email = email or f"{username}@example.com"
    
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    if is_staff:
        user.is_staff = True
        user.is_superuser = True
        user.save()
    
    return user

def create_test_project(user=None, **kwargs):
    """Create a test project with optional parameters"""
    project_data = TestConfig.TEST_PROJECT_DATA.copy()
    project_data.update(kwargs)
    
    project = Project.objects.create(**project_data)
    return project

def create_test_author(**kwargs):
    """Create a test author with optional parameters"""
    author_data = TestConfig.TEST_AUTHOR_DATA.copy()
    author_data.update(kwargs)
    
    author = Author.objects.create(**author_data)
    return author

def create_test_publication(project, **kwargs):
    """Create a test publication with optional parameters"""
    publication_data = TestConfig.TEST_PUBLICATION_DATA.copy()
    publication_data.update(kwargs)
    
    # Handle the author field properly (it's a CharField in the model)
    if 'author' not in publication_data:
        publication_data['author'] = 'Test Author'
    
    # Remove collaborators from kwargs to avoid direct assignment error
    collaborators = kwargs.pop('collaborators', None)
    
    publication = Publication.objects.create(
        project=project,
        **publication_data
    )
    
    # Add collaborators if specified
    if collaborators:
        publication.collaborators.set(collaborators)
    
    return publication

def create_test_file():
    """Create a temporary test file for uploads"""
    return SimpleUploadedFile(
        "test_paper.pdf",
        b"Test PDF content",
        content_type="application/pdf"
    )

# ---------------------------
# Base Test Case
# ---------------------------

@override_settings(SIGNALS_ENABLED=False)
class PublicationLogTestCase(TestCase):
    """Base test case with common setup and utilities"""
    
    def setUp(self):
        """Set up test data for each test"""
        self.client = Client()
        self.user = create_test_user()
        self.project = create_test_project()
        self.author = create_test_author()
    
    def login_user(self, user=None):
        """Helper to login a user"""
        user = user or self.user
        return self.client.login(username=user.username, password=TestConfig.TEST_PASSWORD)

# ---------------------------
# Model Tests
# ---------------------------

class ModelTests(PublicationLogTestCase):
    """Test model functionality and relationships"""
    
    def test_project_creation(self):
        """Test creating a project with all required fields"""
        project = create_test_project(
            title="AI Research Project",
            domain="Artificial Intelligence"
        )
        
        self.assertEqual(project.title, "AI Research Project")
        self.assertEqual(project.domain, "Artificial Intelligence")
        self.assertEqual(str(project), project.title)
    
    def test_publication_creation(self):
        """Test creating a publication with project relationship"""
        publication = create_test_publication(
            self.project,
            title="Machine Learning Paper",
            type="Conference"
        )
        
        self.assertEqual(publication.title, "Machine Learning Paper")
        self.assertEqual(publication.project, self.project)
        self.assertEqual(publication.type, "Conference")
        self.assertEqual(str(publication), publication.title)
    
    def test_author_creation(self):
        """Test creating an author"""
        author = create_test_author(
            name="Dr. Jane Smith",
            email="jane.smith@university.edu"
        )
        
        self.assertEqual(author.name, "Dr. Jane Smith")
        self.assertEqual(author.email, "jane.smith@university.edu")
        self.assertEqual(str(author), author.name)
    
    def test_publication_with_collaborators(self):
        """Test publication with multiple collaborators"""
        author1 = create_test_author(name="Author One")
        author2 = create_test_author(name="Author Two")
        
        publication = create_test_publication(
            self.project,
            collaborators=[author1, author2]
        )
        
        self.assertEqual(publication.collaborators.count(), 2)
        self.assertIn(author1, publication.collaborators.all())
        self.assertIn(author2, publication.collaborators.all())
    
    def test_user_profile_creation(self):
        """Test user profile creation and avatar handling"""
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.user, self.user)
        self.assertFalse(profile.is_online)
        self.assertIsNotNone(profile.get_avatar_url())

# ---------------------------
# View Tests
# ---------------------------

class ViewTests(PublicationLogTestCase):
    """Test view functionality and responses"""
    
    def test_projects_list_view(self):
        """Test the projects list page"""
        response = self.client.get(reverse('projects_page'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/projects_page.html')
        self.assertIn('projects', response.context)
    
    def test_project_detail_view(self):
        """Test the project detail page"""
        response = self.client.get(reverse('project_detail', args=[self.project.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertEqual(response.context['project'], self.project)
    
    def test_publication_list_view(self):
        """Test the publication list page"""
        response = self.client.get(reverse('publication_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/publication_list.html')
        self.assertIn('publications', response.context)
    
    def test_publication_detail_view(self):
        """Test the publication detail page"""
        publication = create_test_publication(self.project)
        response = self.client.get(reverse('publication_detail', args=[publication.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/publication_detail.html')
        self.assertEqual(response.context['publication'], publication)
    
    def test_add_publication_view_requires_login(self):
        """Test that adding publication requires login"""
        response = self.client.get(reverse('add_publication', args=[self.project.pk]))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_add_publication_view_with_login(self):
        """Test adding publication when logged in"""
        self.login_user()
        
        response = self.client.get(reverse('add_publication', args=[self.project.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'publications/add_publication.html')
        self.assertIn('form', response.context)
    
    def test_add_publication_post_valid(self):
        """Test posting valid publication data"""
        self.login_user()
        
        test_file = create_test_file()
        
        data = {
            'title': 'New Test Publication',
            'year': 2024,
            'type': 'Journal',
            'abstract': 'Test abstract',
            'url': 'https://example.com/paper.pdf',
            'new_collaborators': 'Author One, Author Two'
        }
        
        files = {'file': test_file}
        
        response = self.client.post(
            reverse('add_publication', args=[self.project.pk]),
            data,
            files=files,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check if publication was created
        publication = Publication.objects.filter(title='New Test Publication').first()
        self.assertIsNotNone(publication)
        self.assertEqual(publication.project, self.project)
    
    def test_user_dashboard_requires_login(self):
        """Test that user dashboard requires login"""
        response = self.client.get(reverse('user_dashboard'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_user_dashboard_with_login(self):
        """Test user dashboard when logged in"""
        self.login_user()
        
        response = self.client.get(reverse('user_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_dashboard.html')
        self.assertIn('publications', response.context)

# ---------------------------
# Authentication Tests
# ---------------------------

class AuthenticationTests(PublicationLogTestCase):
    """Test authentication functionality"""
    
    def test_signup_view(self):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(reverse('signup'), data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check if user was created
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_login_view(self):
        """Test user login"""
        data = {
            'username': self.user.username,
            'password': TestConfig.TEST_PASSWORD
        }
        
        response = self.client.post(reverse('login'), data, follow=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_logout_view(self):
        """Test user logout"""
        self.login_user()
        
        response = self.client.get(reverse('logout'), follow=True)
        
        self.assertEqual(response.status_code, 200)

# ---------------------------
# Search and Filter Tests
# ---------------------------

class SearchFilterTests(PublicationLogTestCase):
    """Test search and filtering functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create multiple projects and publications for testing
        self.project2 = create_test_project(
            title="Data Science Project",
            domain="Data Science"
        )
        
        self.publication1 = create_test_publication(
            self.project,
            title="AI Research Paper",
            type="Journal"
        )
        
        self.publication2 = create_test_publication(
            self.project2,
            title="Data Analysis Study",
            type="Conference"
        )
    
    def test_project_search(self):
        """Test searching projects by title"""
        response = self.client.get(reverse('projects_page'), {'search': 'AI Research'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)
        
        # Should find the AI project
        projects = response.context['projects']
        self.assertTrue(any('AI Research' in project.title for project in projects))
    
    def test_project_domain_filter(self):
        """Test filtering projects by domain"""
        response = self.client.get(reverse('projects_page'), {'domain': 'Computer Science'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)
        
        # Should only show Computer Science projects
        projects = response.context['projects']
        self.assertTrue(all(project.domain == 'Computer Science' for project in projects))
    
    def test_publication_search(self):
        """Test searching publications by title"""
        response = self.client.get(reverse('publication_list'), {'search': 'AI Research'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('publications', response.context)
        
        # Should find the AI publication
        publications = response.context['publications']
        self.assertTrue(any('AI Research' in pub.title for pub in publications))
    
    def test_publication_type_filter(self):
        """Test filtering publications by type"""
        response = self.client.get(reverse('publication_list'), {'type': 'Journal'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('publications', response.context)
        
        # Should only show Journal publications
        publications = response.context['publications']
        self.assertTrue(all(pub.type == 'Journal' for pub in publications))
    
    def test_publication_year_filter(self):
        """Test filtering publications by year"""
        response = self.client.get(reverse('publication_list'), {'year': '2024'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('publications', response.context)
        
        # Should only show 2024 publications
        publications = response.context['publications']
        self.assertTrue(all(pub.year == 2024 for pub in publications))

# ---------------------------
# Form Tests
# ---------------------------

class FormTests(PublicationLogTestCase):
    """Test form validation and functionality"""
    
    def test_publication_form_valid(self):
        """Test valid publication form data"""
        from .forms import PublicationForm
        
        test_file = create_test_file()
        
        data = {
            'title': 'Test Publication',
            'year': 2024,
            'type': 'Journal',
            'abstract': 'Test abstract',
            'url': 'https://example.com/paper.pdf',
            'new_collaborators': 'Author One, Author Two'
        }
        
        files = {'file': test_file}
        
        form = PublicationForm(data, files, project=self.project)
        
        self.assertTrue(form.is_valid())
    
    def test_publication_form_invalid_no_file_or_url(self):
        """Test publication form validation when neither file nor URL is provided"""
        from .forms import PublicationForm
        
        data = {
            'title': 'Test Publication',
            'year': 2024,
            'type': 'Journal',
            'abstract': 'Test abstract',
            'new_collaborators': 'Author One'
        }
        
        form = PublicationForm(data, project=self.project)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Please upload a file or provide a download link', str(form.errors))
    
    def test_user_creation_form_valid(self):
        """Test valid user creation form data"""
        from .forms import UserCreation
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        form = UserCreation(data)
        
        self.assertTrue(form.is_valid())
    
    def test_user_creation_form_duplicate_email(self):
        """Test user creation form with duplicate email"""
        from .forms import UserCreation
        
        # Create a user with the email first
        create_test_user(email='existing@example.com')
        
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        form = UserCreation(data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

# ---------------------------
# Integration Tests
# ---------------------------

class IntegrationTests(PublicationLogTestCase):
    """Test complete workflows and integrations"""
    
    def test_complete_publication_workflow(self):
        """Test the complete workflow from project creation to publication"""
        # 1. Create a project
        project = create_test_project(
            title="Integration Test Project",
            domain="Integration Testing"
        )
        
        # 2. Create an author
        author = create_test_author(
            name="Integration Test Author",
            email="integration@test.com"
        )
        
        # 3. Login and add publication
        self.login_user()
        
        test_file = create_test_file()
        
        data = {
            'title': 'Integration Test Publication',
            'year': 2024,
            'type': 'Journal',
            'abstract': 'Integration test abstract',
            'url': 'https://example.com/integration.pdf',
            'new_collaborators': 'Integration Test Author'
        }
        
        files = {'file': test_file}
        
        response = self.client.post(
            reverse('add_publication', args=[project.pk]),
            data,
            files=files,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify publication was created with correct relationships
        publication = Publication.objects.filter(title='Integration Test Publication').first()
        self.assertIsNotNone(publication)
        self.assertEqual(publication.project, project)
        self.assertEqual(publication.collaborators.count(), 1)
        self.assertEqual(publication.collaborators.first().name, 'Integration Test Author')
        
        # 5. Verify it appears in publication list
        response = self.client.get(reverse('publication_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(publication, response.context['publications'])
        
        # 6. Verify it appears in project detail
        response = self.client.get(reverse('project_detail', args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(publication, response.context['publications'])
    
    def test_user_registration_and_dashboard_access(self):
        """Test user registration and subsequent dashboard access"""
        # 1. Register new user
        username = TestConfig.get_unique_username()
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'password1': 'DashboardPass123!',
            'password2': 'DashboardPass123!'
        }
        
        response = self.client.post(reverse('signup'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 2. Login
        login_data = {
            'username': username,
            'password': 'DashboardPass123!'
        }
        
        response = self.client.post(reverse('login'), login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # 3. Access dashboard
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/user_dashboard.html')

# ---------------------------
# Edge Case Tests
# ---------------------------

class EdgeCaseTests(PublicationLogTestCase):
    """Test edge cases and error conditions"""
    
    def test_publication_without_project(self):
        """Test that publication requires a project"""
        with self.assertRaises(Exception):
            Publication.objects.create(
                title="Test Publication",
                year=2024,
                type="Journal",
                author="Test Author"
            )
    
    def test_author_without_name(self):
        """Test author creation with null name (should be allowed based on model)"""
        author = Author.objects.create(
            name=None,
            email="test@example.com"
        )
        
        self.assertIsNone(author.name)
        self.assertEqual(author.email, "test@example.com")
    
    def test_duplicate_author_name(self):
        """Test that author names must be unique"""
        author1 = create_test_author(name="Unique Author")
        
        # This should fail due to unique constraint
        with self.assertRaises(Exception):
            Author.objects.create(
                name="Unique Author",
                email="different@example.com"
            )
    
    def test_publication_validation_without_file_or_url(self):
        """Test publication model validation"""
        publication = Publication(
            project=self.project,
            title="Test Publication",
            year=2024,
            type="Journal",
            author="Test Author"
        )
        
        # Should raise validation error
        with self.assertRaises(Exception):
            publication.full_clean()
    
    def test_large_file_upload(self):
        """Test handling of large file uploads"""
        self.login_user()
        
        # Create a large file (simulated)
        large_file = SimpleUploadedFile(
            "large_paper.pdf",
            b"x" * 1024 * 1024,  # 1MB file
            content_type="application/pdf"
        )
        
        data = {
            'title': 'Large File Test',
            'year': 2024,
            'type': 'Journal',
            'abstract': 'Test with large file',
            'new_collaborators': 'Test Author'
        }
        
        files = {'file': large_file}
        
        response = self.client.post(
            reverse('add_publication', args=[self.project.pk]),
            data,
            files=files,
            follow=True
        )
        
        # Should handle large files gracefully
        self.assertEqual(response.status_code, 200)

# ---------------------------
# Performance Tests
# ---------------------------

class PerformanceTests(PublicationLogTestCase):
    """Test performance with larger datasets"""
    
    def test_multiple_publications_performance(self):
        """Test performance with many publications"""
        # Create many publications
        publications = []
        for i in range(50):
            publication = create_test_publication(
                self.project,
                title=f"Publication {i}",
                year=2024
            )
            publications.append(publication)
        
        # Test publication list performance
        response = self.client.get(reverse('publication_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['publications']), 50)
    
    def test_search_performance(self):
        """Test search performance with many records"""
        # Create many publications with searchable titles
        for i in range(100):
            create_test_publication(
                self.project,
                title=f"Research Paper {i}",
                year=2024
            )
        
        # Test search performance
        response = self.client.get(reverse('publication_list'), {'search': 'Research'})
        
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['publications']), 0)

# ---------------------------
# Cleanup
# ---------------------------

def tearDownModule():
    """Clean up any temporary files created during testing"""
    # This will be called after all tests in this module
    pass
