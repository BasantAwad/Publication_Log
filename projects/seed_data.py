import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projects.settings")  # CHANGE THIS
django.setup()

from projects.models import Project, Author, Publication, HarvestMatchCandidate, MatchRequest

# Clear existing data (optional)
# Project.objects.all().delete()
# Author.objects.all().delete()
# Publication.objects.all().delete()
# HarvestMatchCandidate.objects.all().delete()
# MatchRequest.objects.all().delete()

# Helper for random date
def random_date():
    return date.today() - timedelta(days=random.randint(0, 1000))

# 1. Create Authors
authors = []
for i in range(15):
    a = Author.objects.create(
        name=f"Author {i+1}",
        email=f"author{i+1}@gmail.com"
    )
    authors.append(a)

# 2. Create Projects
projects = []
for i in range(15):
    p = Project.objects.create(
        title=f"Project {i+1}",
        created=random_date(),
        team=f"Team {i+1}",
        abstract=f"This is the abstract for project {i+1}.",
        duration=f"{random.randint(6, 36)} months",
        domain="AI",
        scientific_case=f"Scientific case for project {i+1}"
    )
    projects.append(p)

# 3. Create Publications
publications = []
for i in range(15):
    pub = Publication.objects.create(
        project=random.choice(projects),
        title=f"Publication {i+1}",
        author=random.choice(authors).name,
        url=f"https://example.com/publication{i+1}",
        year=random.randint(2015, 2025),
        type=random.choice([t[0] for t in Publication._meta.get_field('type').choices]),
        abstract=f"Abstract for publication {i+1}"
    )
    # Add 1-3 collaborators
    pub.collaborators.set(random.sample(authors, random.randint(1, 3)))
    pub.save()
    publications.append(pub)

# 4. Create HarvestMatchCandidate
for i in range(15):
    HarvestMatchCandidate.objects.create(
        publication=random.choice(publications),
        project=random.choice(projects),
        matched_by_ai=random.choice([True, False]),
        confirmed_by_admin=random.choice([True, False, None]),
        confidence_score=round(random.uniform(0.5, 1.0), 2)
    )

# 5. Create MatchRequests
for i in range(15):
    MatchRequest.objects.create(
        project=random.choice(projects),
        publication=random.choice(publications),
        match_title=f"Match Title {i+1}",
        match_score=round(random.uniform(0.5, 1.0), 2),
        match_authors=", ".join([a.name for a in random.sample(authors, 2)]),
        approved=random.choice([True, False, None])
    )

print("✅ Dummy data inserted successfully!")
