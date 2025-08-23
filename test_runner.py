#!/usr/bin/env python
"""
Simple test runner to check if the basic model tests work
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase
from projects.models import Project, Publication, Author
from datetime import date

class SimpleModelTest(TestCase):
    def test_basic_models(self):
        """Test basic model creation"""
        # Test Project creation
        project = Project.objects.create(
            title="Test Project",
            created=date(2024, 1, 15),
            team="Test Team",
            abstract="Test abstract",
            duration="6 months",
            domain="Computer Science",
            scientific_case="Test case"
        )
        self.assertEqual(project.title, "Test Project")
        
        # Test Author creation
        author = Author.objects.create(
            name="Test Author",
            email="test@example.com"
        )
        self.assertEqual(author.name, "Test Author")
        
        # Test Publication creation
        publication = Publication.objects.create(
            project=project,
            title="Test Publication",
            year=2024,
            type="Journal",
            author="Test Author",
            url="https://example.com/paper.pdf"
        )
        self.assertEqual(publication.title, "Test Publication")
        self.assertEqual(publication.project, project)
        
        print("✅ All basic model tests passed!")

if __name__ == "__main__":
    # Run the test
    test = SimpleModelTest()
    test.setUp()
    test.test_basic_models()
    print("Test completed successfully!")
