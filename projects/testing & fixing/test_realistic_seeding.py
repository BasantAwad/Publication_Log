#!/usr/bin/env python
"""
Test script to demonstrate realistic database seeding
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from realistic_data import (
    ACADEMIC_INSTITUTIONS, DEPARTMENTS, FUNDING_SOURCES,
    REAL_PUBLICATION_TITLES, RESEARCH_DOMAINS, FAMOUS_RESEARCHERS
)

def test_realistic_data():
    """Test the realistic data imports"""
    print("=== Realistic Database Seeding Test ===\n")
    
    print("📚 Real Academic Institutions:")
    for i, institution in enumerate(ACADEMIC_INSTITUTIONS[:5], 1):
        print(f"  {i}. {institution}")
    print(f"  ... and {len(ACADEMIC_INSTITUTIONS) - 5} more\n")
    
    print("🔬 Real Research Departments:")
    for dept in DEPARTMENTS:
        print(f"  • {dept}")
    print()
    
    print("💰 Real Funding Sources:")
    for i, source in enumerate(FUNDING_SOURCES[:5], 1):
        print(f"  {i}. {source}")
    print(f"  ... and {len(FUNDING_SOURCES) - 5} more\n")
    
    print("👨‍🔬 Famous Researchers (some will be used as authors):")
    for i, researcher in enumerate(FAMOUS_RESEARCHERS[:10], 1):
        print(f"  {i}. {researcher}")
    print(f"  ... and {len(FAMOUS_RESEARCHERS) - 10} more\n")
    
    print("📖 Real Publication Titles by Domain:")
    for domain, titles in REAL_PUBLICATION_TITLES.items():
        print(f"\n  {domain}:")
        for i, title in enumerate(titles[:3], 1):
            print(f"    {i}. {title}")
        if len(titles) > 3:
            print(f"    ... and {len(titles) - 3} more")
    
    print("\n" + "="*50)
    print("✅ Realistic data is ready for database seeding!")
    print("\nTo run the realistic seeding:")
    print("python manage.py seed_db --authors 50 --publications-per-domain 8")
    print("\nThis will create:")
    print("• Authors with real academic institutions and departments")
    print("• Publications with actual research paper titles")
    print("• Realistic abstracts based on domain-specific templates")
    print("• Famous researchers as some of the authors")
    print("• Proper research interests and keywords")

if __name__ == "__main__":
    test_realistic_data()
