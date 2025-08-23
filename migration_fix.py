#!/usr/bin/env python
"""
Migration script to fix the database schema and migrate existing data
"""
import os
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import Publication, Author, Project

def fix_database_schema():
    """Fix the database schema by creating a new author field and migrating data"""
    
    print("Starting database schema fix...")
    
    # Create a default author if none exists
    default_author, created = Author.objects.get_or_create(
        name="Unknown Author",
        defaults={
            'email': 'unknown@example.com',
            'institution': 'Unknown Institution',
            'department': 'Unknown Department'
        }
    )
    
    if created:
        print(f"Created default author: {default_author.name}")
    
    # Get all publications that need fixing
    publications = Publication.objects.all()
    print(f"Found {publications.count()} publications to process...")
    
    for pub in publications:
        try:
            # Check if publication has a valid primary_author
            if not hasattr(pub, 'primary_author') or pub.primary_author is None:
                # Try to extract author name from the old author field if it exists
                if hasattr(pub, 'author') and pub.author:
                    # Try to find existing author by name
                    author_name = str(pub.author)
                    author, created = Author.objects.get_or_create(
                        name=author_name,
                        defaults={
                            'email': f"{author_name.lower().replace(' ', '.')}@example.com",
                            'institution': 'Unknown Institution',
                            'department': 'Unknown Department'
                        }
                    )
                    pub.primary_author = author
                    print(f"Fixed publication '{pub.title}' with author: {author.name}")
                else:
                    # Use default author
                    pub.primary_author = default_author
                    print(f"Fixed publication '{pub.title}' with default author")
                
                pub.save()
        
        except Exception as e:
            print(f"Error fixing publication {pub.id}: {e}")
    
    print("Database schema fix completed!")

def create_migration():
    """Create and run migrations"""
    print("Creating migrations...")
    os.system("python manage.py makemigrations")
    print("Running migrations...")
    os.system("python manage.py migrate")

if __name__ == "__main__":
    print("Starting database migration process...")
    
    # First create and run migrations
    create_migration()
    
    # Then fix the data
    fix_database_schema()
    
    print("Migration process completed!")
