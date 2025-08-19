import os
import random
import datetime
import requests
from faker import Faker
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from projects.models import Project, Author, Publication, HarvestMatchCandidate, MatchRequest

fake = Faker()

# Dictionary mapping research domains to their descriptions, images, and keywords
RESEARCH_DOMAINS = {
    # Each domain contains a description, an image placeholder URL, and a list of keywords
    "Machine Learning": {
        "description": "Advancing algorithms and models that enable computers to learn from data",
        "image": "https://placehold.co/600x400/3a86ff/white?text=Machine+Learning",
        "keywords": ["deep learning", "neural networks", "computer vision", "NLP"]
    },
    # ... other domains omitted for brevity ...
    "Cybersecurity": {
        "description": "Protecting systems and networks from digital attacks",
        "image": "https://placehold.co/600x400/f44336/white?text=Cybersecurity",
        "keywords": ["cryptography", "network security", "penetration testing", "threat intelligence"]
    }
}

# Dictionary mapping domains to lists of realistic publication titles
PUBLICATION_TITLES = {
    "Machine Learning": [
        "Attention Is All You Need",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        # ... other titles ...
    ],
    # ... other domains omitted for brevity ...
}

# Dictionary mapping domains to lists of image URLs
DOMAIN_IMAGES = {
    "Machine Learning": [
        "https://images.unsplash.com/photo-1629904853893-c2c8981a1dc5",
        # ... other images ...
    ],
    # ... other domains omitted for brevity ...
}

# Templates for sample PDF content (LaTeX format)
PDF_TEMPLATES = {
    "Journal": """
    \\documentclass{{article}}
    \\usepackage{{graphicx}}
    \\title{{{title}}}
    \\author{{{authors}}}
    \\date{{{year}}}
    
    \\begin{{document}}
    \\maketitle
    
    \\section{{Abstract}}
    {abstract}
    
    \\section{{Introduction}}
    This paper addresses {key_challenge} in {domain}. Recent advances have enabled new approaches, but
    limitations remain in {limitation_area}.
    
    \\section{{Methods}}
    We developed a novel approach combining {method1} with {method2},
    implemented using {framework}.
    
    \\section{{Results}}
    Our evaluation shows {percentage}\\% improvement in {metric} compared to
    existing techniques ({p_value}).
    
    \\section{{Conclusion}}
    These findings demonstrate significant advances in {domain}, opening new
    directions including {future_work}.
    \\end{{document}}
    """,
    "Conference": """
    \\documentclass{{acmart}}
    \\title{{{title}}}
    \\author{{{authors}}}
    \\setcopyright{{rightsretained}}
    
    \\begin{{document}}
    \\maketitle
    
    \\begin{{abstract}}
    {abstract}
    \\end{{abstract}}
    
    \\section{{Introduction}}
    The field of {domain} faces growing challenges with {challenge}. We present...
    \\section{{Related Work}}
    Prior approaches include {approach1} and {approach2}, but lack {limitation}...
    \\end{{document}}
    """
}

# List of academic and personal email domains
EMAIL_DOMAINS = [
    "harvard.edu", "mit.edu", "stanford.edu", "ox.ac.uk", 
    # ... other domains ...
    "gmail.com", "outlook.com", "yahoo.com", "protonmail.com",
    # ... other personal domains ...
]

class Command(BaseCommand):
    help = 'Seed database with comprehensive research domain data'

    def handle(self, *args, **kwargs):
        # Entry point for Django management command 'seed_db'
        self.stdout.write("Starting database seeding...")
        os.environ["SEEDING"] = "true"  # Set environment variable for seeding
        self.seed_authors()             # Create authors
        self.seed_domain_projects()     # Create domain projects
        self.seed_publications()        # Create publications for each domain
        self.stdout.write(self.style.SUCCESS('Database successfully seeded with realistic research data!'))

    def generate_abstract(self, domain):
        """Generate a realistic abstract text for a publication in a given domain."""
        keywords = RESEARCH_DOMAINS[domain]["keywords"]
        methods = random.choice([
            f"using {random.choice(keywords)} and {random.choice(keywords)}",
            f"combining {random.choice(keywords)} with {random.choice(keywords)}",
            f"through novel application of {random.choice(keywords)}"
        ])
        # Combine elements into a sentence for the abstract
        return (
            f"This study addresses critical challenges in {domain.lower()} {methods}. "
            f"Our approach demonstrates significant improvements in {random.choice(['efficiency', 'accuracy', 'scalability'])} "
            f"compared to existing methods. The results have important implications for {random.choice(keywords)} "
            f"and open new directions for future research in {domain.lower()}."
        )

    def download_file(self, url, model_instance, field_name):
        """Download a file from a URL and attach it to a file/image field on a model instance."""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = os.path.basename(url.split('?')[0])
                getattr(model_instance, field_name).save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )
                return True
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Couldn't download {url}: {e}"))
        return False

    def generate_pdf(self, publication):
        """Generate PDF content for a publication based on its type and domain."""
        template = PDF_TEMPLATES.get(publication.type, PDF_TEMPLATES["Journal"])
        keywords = RESEARCH_DOMAINS[publication.project.domain]["keywords"]
        
        # Fill in the template with random values and publication info
        content = template.format(
            title=publication.title,
            authors=publication.author + " et al.",
            year=publication.year,
            abstract=publication.abstract,
            domain=publication.project.domain.lower(),
            key_challenge=random.choice(keywords),
            limitation_area=random.choice(keywords),
            method1=random.choice(keywords),
            method2=random.choice(keywords),
            framework="TensorFlow" if "Machine Learning" in publication.project.domain else "Qiskit",
            percentage=random.randint(5, 78),
            metric=random.choice(["accuracy", "F1 score", "latency"]),
            p_value=f"p<0.0{random.randint(1,5)}",
            future_work=random.choice(keywords) + " applications",
            challenge=random.choice(keywords) + " scaling issues",
            approach1=random.choice(keywords),
            approach2=random.choice(keywords),
            limitation=random.choice(keywords)
        )
        
        filename = f"{publication.title.replace(' ', '_')[:50]}.pdf"
        return ContentFile(content.encode('utf-8'), name=filename)

    def seed_authors(self):
        """Create 200 authors with realistic (academic or personal) email addresses."""
        self.stdout.write("Creating authors with realistic email addresses...")
        
        for i in range(200):
            # Generate unique names
            first_name = fake.unique.first_name()
            last_name = fake.unique.last_name()
            
            # 70% chance to use academic domain, otherwise personal domain
            if random.random() < 0.7:
                domain = random.choice([d for d in EMAIL_DOMAINS if d.endswith('.edu') or d.endswith('.ac.uk')])
                email = f"{first_name[0].lower()}{last_name.lower()}@{domain}"
            else:
                domain = random.choice([d for d in EMAIL_DOMAINS if not (d.endswith('.edu') or d.endswith('.ac.uk'))])
                if random.random() < 0.5:
                    email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
                else:
                    email = f"{first_name.lower()}{random.randint(1,99)}@{domain}"
            
            # Create the Author object
            Author.objects.create(
                name=f"{first_name} {last_name}",
                email=email
            )
            
            # Progress output for every 50 authors
            if (i+1) % 50 == 0:
                self.stdout.write(f"Created {i+1} authors...")

    def seed_domain_projects(self):
        """Create a Project for each research domain."""
        self.stdout.write("Setting up research domain projects...")
        
        for domain, details in RESEARCH_DOMAINS.items():
            # Random start date between 2015 and today
            start_date = fake.date_between(
                start_date=datetime.date(2015, 1, 1),
                end_date='today'
            )
            # Random duration between 2 and 5 years
            duration_years = random.randint(2, 5)
            
            # Create Project object for the domain
            Project.objects.create(
                title=domain,
                created=start_date,
                team=f"{domain} Research Network",
                abstract=details["description"],
                duration=f"{duration_years} years",
                domain=domain,
                scientific_case=(
                    f"This project coordinates research efforts in {domain.lower()}, focusing on: "
                    f"{', '.join(details['keywords'][:3])}. Our consortium brings together experts "
                    f"from academia and industry to advance this critical field."
                )
            )
            self.stdout.write(f"Created project: {domain}")

    def seed_publications(self):
        """Create several publications for each research domain project."""
        self.stdout.write("Adding realistic publications to each domain...")
        
        for domain, titles in PUBLICATION_TITLES.items():
            project = Project.objects.get(title=domain)
            authors = list(Author.objects.all())
            
            for title in titles:
                # Create a publication year within 3 years after project start
                pub_year = project.created.year + random.randint(0, min(3, datetime.date.today().year - project.created.year))
                
                # Create Publication object
                pub = Publication(
                    project=project,
                    title=title,
                    author=random.choice(authors).name,
                    abstract=self.generate_abstract(domain),
                    year=pub_year,
                    url=f"https://doi.org/{random.randint(10,99)}.{random.randint(1000,9999)}",  # Fake DOI
                    type=random.choice(["Journal", "Conference", "Preprint"]),
                )
                pub.save()

                # Generate and attach a PDF file to the publication
                pdf_content = self.generate_pdf(pub)
                pub.file.save(f"{pub.title[:50]}.pdf", pdf_content)
                # Download and attach an image from domain-specific images
                if domain in DOMAIN_IMAGES:
                    image_url = random.choice(DOMAIN_IMAGES[domain]) + f"?{random.randint(1000,9999)}"
                    self.download_file(image_url, pub, 'image')

                # Add 2-5 collaborators (authors) to the publication
                collaborators = random.choices(authors, k=random.randint(2,5))
                pub.collaborators.add(*collaborators)
                
                # Create match records for recent publications
                self.create_matching_records(pub, project)
                
            self.stdout.write(f"Added {len(titles)} publications to {domain}")

    def create_matching_records(self, publication, project):
        """Create HarvestMatchCandidate and MatchRequest records for publications."""
        if random.random() > 0.3:  # 70% chance to create a match candidate
            HarvestMatchCandidate.objects.create(
                publication=publication,
                project=project,
                matched_by_ai=True,
                confidence_score=random.uniform(0.7, 0.99),
                created_at=fake.date_time_between(
                    start_date=datetime.datetime(publication.year, 1, 1),
                    end_date='now'
                )
            )
            if random.random() > 0.4:  # 60% chance to create a match request
                shared_authors = random.sample(
                    list(publication.collaborators.all()),
                    min(2, publication.collaborators.count())
                )
                MatchRequest.objects.create(
                    project=project,
                    publication=publication,
                    match_title=publication.title,
                    match_score=random.uniform(0.7, 0.95),
                    match_authors=", ".join(a.name for a in shared_authors),
                    approved=random.choice([True, False, None])
                )

# Allow running this file standalone for debugging (not typical for Django management commands)
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    import django
    django.setup()