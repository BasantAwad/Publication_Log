import os
import random
import datetime
import requests
from faker import Faker
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from projects.models import Project, Author, Publication, HarvestMatchCandidate, MatchRequest

fake = Faker()

# Expanded research domains with descriptions and images
RESEARCH_DOMAINS = {
    "Machine Learning": {
        "description": "Advancing algorithms and models that enable computers to learn from data",
        "image": "https://placehold.co/600x400/3a86ff/white?text=Machine+Learning",
        "keywords": ["deep learning", "neural networks", "computer vision", "NLP"]
    },
    "Quantum Computing": {
        "description": "Developing quantum systems for computation and information processing",
        "image": "https://placehold.co/600x400/9c27b0/white?text=Quantum+Computing",
        "keywords": ["qubits", "quantum algorithms", "quantum supremacy", "error correction"]
    },
    "Biomedical Engineering": {
        "description": "Applying engineering principles to healthcare and medical technologies",
        "image": "https://placehold.co/600x400/4caf50/white?text=Biomedical+Eng",
        "keywords": ["biomaterials", "medical devices", "tissue engineering", "biomechanics"]
    },
    "Climate Science": {
        "description": "Studying climate systems and developing solutions for climate change",
        "image": "https://placehold.co/600x400/009688/white?text=Climate+Science",
        "keywords": ["global warming", "carbon capture", "climate modeling", "renewables"]
    },
    "Neuroscience": {
        "description": "Understanding the nervous system and brain function",
        "image": "https://placehold.co/600x400/673ab7/white?text=Neuroscience",
        "keywords": ["cognitive science", "neuroimaging", "neural circuits", "brain-computer interface"]
    },
    "Robotics": {
        "description": "Designing and programming robots for various applications",
        "image": "https://placehold.co/600x400/607d8b/white?text=Robotics",
        "keywords": ["autonomous systems", "human-robot interaction", "robot learning", "swarm robotics"]
    },
    "Cybersecurity": {
        "description": "Protecting systems and networks from digital attacks",
        "image": "https://placehold.co/600x400/f44336/white?text=Cybersecurity",
        "keywords": ["cryptography", "network security", "penetration testing", "threat intelligence"]
    }
}



# Expanded publication titles with realistic papers in each domain
PUBLICATION_TITLES = {
    "Machine Learning": [
        "Attention Is All You Need",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        "Generative Adversarial Networks",
        "Deep Residual Learning for Image Recognition",
        "Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context",
        "ALBERT: A Lite BERT for Self-Supervised Learning of Language Representations",
        "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks"
    ],
    "Quantum Computing": [
        "Quantum Supremacy Using Programmable Processor",
        "Noisy Intermediate-Scale Quantum Algorithms",
        "Quantum Error Correction with Superconducting Qubits",
        "Quantum Machine Learning: A Classical Perspective",
        "Variational Quantum Algorithms",
        "Quantum Computational Advantage with Programmable Photonic Processors"
    ],
    "Biomedical Engineering": [
        "CRISPR-Cas9 Mediated Genome Editing",
        "Organ-on-a-Chip Technologies for Drug Screening",
        "Engineered Antibodies for Cancer Immunotherapy",
        "3D Bioprinting of Tissues and Organs",
        "Neural Dust: Ultrasonic Backscatter for Wireless Power and Communication",
        "Wearable Biosensors for Health Monitoring"
    ],
    "Climate Science": [
        "The Global Carbon Budget 1959-2023",
        "Sixth Assessment Report of the IPCC",
        "Climate Impacts of Aerosol-Cloud Interactions",
        "Arctic Amplification of Climate Change",
        "Ocean Acidification and Marine Ecosystems",
        "Tipping Elements in the Earth's Climate System"
    ],
    "Neuroscience": [
        "The Connectome of an Insect Brain",
        "Closed-Loop Deep Brain Stimulation for Parkinson's Disease",
        "Neural Correlates of Consciousness",
        "Optogenetic Control of Neural Circuits",
        "Artificial Vision Through Brain-Machine Interfaces",
        "A Molecular Atlas of Cell Types in the Brain"
    ],
    "Robotics": [
        "Learning Dexterous In-Hand Manipulation",
        "Self-Supervised Learning for Robotic Grasping",
        "Human-Robot Collaboration in Manufacturing",
        "Autonomous Driving in Urban Environments",
        "Soft Robotics: Challenges and Perspectives",
        "Swarm Robotics: From Algorithms to Applications"
    ],
    "Cybersecurity": [
        "Adversarial Machine Learning: A Security Perspective",
        "Zero Trust Architecture for Enterprise Networks",
        "Post-Quantum Cryptography: Algorithms and Implementation",
        "Threat Detection Using Machine Learning",
        "Mitigating Advanced Persistent Threats",
        "Blockchain for Secure Identity Management"
    ]
}
DOMAIN_IMAGES = {
    "Machine Learning": [
        "https://images.unsplash.com/photo-1629904853893-c2c8981a1dc5",  # AI visualization
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485",  # Neural network
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71"     # Data analysis
    ],
    "Quantum Computing": [
        "https://images.unsplash.com/photo-1620708619271-b62cd87b7c3a",  # Quantum chip
        "https://images.unsplash.com/photo-1626908013355-87b22d52a7e1",  # Qubits visualization
        "https://images.unsplash.com/photo-1579829366248-204fe8413f31"   # Quantum computing lab
    ],
    "Biomedical Engineering": [
        "https://images.unsplash.com/photo-1579684385127-1ef15d508118",  # Medical devices
        "https://images.unsplash.com/photo-1579165466741-92080800211f",  # Lab equipment
        "https://images.unsplash.com/photo-1607619056574-6e1c20937f11"   # Cell research
    ],
    "Climate Science": [
        "https://images.unsplash.com/photo-1618773928121-c32242e63f39",  # Solar panels
        "https://images.unsplash.com/photo-1617791160536-598cf32026fb",  # Wind turbines
        "https://images.unsplash.com/photo-1615751072497-5f5169febe17"   # Climate change
    ],
    "Neuroscience": [
        "https://images.unsplash.com/photo-1622445275483-3b4fff140a30",  # Brain scan
        "https://images.unsplash.com/photo-1617791160505-6f00504e3519",  # Neurons
        "https://images.unsplash.com/photo-1582719471382-82782f7738ec"   # Neuroscience lab
    ],
    "Robotics": [
        "https://images.unsplash.com/photo-1592837380613-56495d343e91",  # Humanoid robot
        "https://images.unsplash.com/photo-1593504049359-9b616e593690",  # Robotic arm
        "https://images.unsplash.com/photo-1620712943543-9921fff9b0bc"   # AI robotics
    ],
    "Cybersecurity": [
        "https://images.unsplash.com/photo-1560732488-6b0df2402548",  # Digital security
        "https://images.unsplash.com/photo-1605787020600-b9ebd5df1d14",  # Hacker terminal
        "https://images.unsplash.com/photo-1550751827-4d374728efce"   # Data protection
    ],
    "Computer Vision": [
        "https://images.unsplash.com/photo-1622822223747-d3cdcc6f4925",  # Facial recognition
        "https://images.unsplash.com/photo-1620712943543-9921fff9b0bb",  # Object detection
        "https://images.unsplash.com/photo-1620712943543-9921fff9b0aa"   # Image processing
    ],
    "Renewable Energy": [
        "https://images.unsplash.com/photo-1508514177221-188e1afc5f84",  # Solar farm
        "https://images.unsplash.com/photo-1508514177221-188e1afc5000",  # Wind farm
        "https://images.unsplash.com/photo-1508514177221-188e1af50001"   # Hydroelectric
    ],
    "Artificial Intelligence": [
        "https://images.unsplash.com/photo-1677442135131-2518d7773855",  # AI chip
        "https://images.unsplash.com/photo-1677442135131-2518d7773856",  # Deep learning
        "https://images.unsplash.com/photo-1677442135131-2518d7773857"   # Robotics
    ]
}


# Sample PDF content templates
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


# Mixed academic and personal email domains
EMAIL_DOMAINS = [
    # Academic
    "harvard.edu", "mit.edu", "stanford.edu", "ox.ac.uk", 
    "cam.ac.uk", "berkeley.edu", "princeton.edu", "yale.edu",
    "ucl.ac.uk", "ethz.ch", "epfl.ch", "utoronto.ca",
    "kyoto-u.ac.jp", "tsinghua.edu.cn", "nus.edu.sg",
    
    # Personal
    "gmail.com", "outlook.com", "yahoo.com", "protonmail.com",
    "icloud.com", "hotmail.com", "zoho.com"
]

class Command(BaseCommand):
    help = 'Seed database with comprehensive research domain data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding...")
        os.environ["SEEDING"] = "true"
        self.seed_authors()
        self.seed_domain_projects()
        self.seed_publications()
        self.stdout.write(self.style.SUCCESS('Database successfully seeded with realistic research data!'))

    def generate_abstract(self, domain):
        """Generate domain-specific abstract using keywords"""
        keywords = RESEARCH_DOMAINS[domain]["keywords"]
        methods = random.choice([
            f"using {random.choice(keywords)} and {random.choice(keywords)}",
            f"combining {random.choice(keywords)} with {random.choice(keywords)}",
            f"through novel application of {random.choice(keywords)}"
        ])
        
        return (
            f"This study addresses critical challenges in {domain.lower()} {methods}. "
            f"Our approach demonstrates significant improvements in {random.choice(['efficiency', 'accuracy', 'scalability'])} "
            f"compared to existing methods. The results have important implications for {random.choice(keywords)} "
            f"and open new directions for future research in {domain.lower()}."
        )

    def download_file(self, url, model_instance, field_name):
        """Download and attach a file to model instance"""
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
        """Generate realistic PDF content for the publication"""
        template = PDF_TEMPLATES.get(publication.type, PDF_TEMPLATES["Journal"])
        keywords = RESEARCH_DOMAINS[publication.project.domain]["keywords"]
        
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
        """Create 200 authors with mixed academic/personal emails"""
        self.stdout.write("Creating authors with realistic email addresses...")
        
        for i in range(200):
            # Ensure unique names
            first_name = fake.unique.first_name()
            last_name = fake.unique.last_name()
            
            # 70% academic emails, 30% personal
            if random.random() < 0.7:
                # Academic email pattern
                domain = random.choice([d for d in EMAIL_DOMAINS if d.endswith('.edu') or d.endswith('.ac.uk')])
                email = f"{first_name[0].lower()}{last_name.lower()}@{domain}"
            else:
                # Personal email pattern
                domain = random.choice([d for d in EMAIL_DOMAINS if not (d.endswith('.edu') or d.endswith('.ac.uk'))])
                if random.random() < 0.5:
                    email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
                else:
                    email = f"{first_name.lower()}{random.randint(1,99)}@{domain}"
            
            Author.objects.create(
                name=f"{first_name} {last_name}",
                email=email
            )
            
            if (i+1) % 50 == 0:
                self.stdout.write(f"Created {i+1} authors...")

    def seed_domain_projects(self):
        """Create the main research domain projects"""
        self.stdout.write("Setting up research domain projects...")
        
        for domain, details in RESEARCH_DOMAINS.items():
            # Random start date between 2015-2023
            start_date = fake.date_between(
                start_date=datetime.date(2015, 1, 1),
                end_date='today'
            )
            
            # Project duration (2-5 years)
            duration_years = random.randint(2, 5)
            
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
        """Add publications to each domain"""
        self.stdout.write("Adding realistic publications to each domain...")
        
        for domain, titles in PUBLICATION_TITLES.items():
            project = Project.objects.get(title=domain)
            authors = list(Author.objects.all())
            
            for title in titles:
                # Create realistic publication date (after project start)
                pub_year = project.created.year + random.randint(0, min(3, datetime.date.today().year - project.created.year))
                
                pub = Publication(
                    project=project,
                    title=title,
                    author=random.choice(authors).name,
                    abstract=self.generate_abstract(domain),
                    year=pub_year,
                    url=f"https://doi.org/{random.randint(10,99)}.{random.randint(1000,9999)}",  # Fake DOI
                    type=random.choice(["Journal", "Conference", "Preprint"]),
                    # image would be handled via file fields
                )
                pub.save()

                 # Add PDF file
                pdf_content = self.generate_pdf(pub)
                pub.file.save(f"{pub.title[:50]}.pdf", pdf_content)
                # Add image from domain-specific collection
                if domain in DOMAIN_IMAGES:
                    image_url = random.choice(DOMAIN_IMAGES[domain]) + f"?{random.randint(1000,9999)}"
                    self.download_file(image_url, pub, 'image')

                
                # Add 2-5 collaborators (more likely to be academic emails)
                collaborators = random.choices(authors, k=random.randint(2,5))
                pub.collaborators.add(*collaborators)
                
                # Create matching records with higher probability for recent publications
                self.create_matching_records(pub, project)
                
            self.stdout.write(f"Added {len(titles)} publications to {domain}")

    def create_matching_records(self, publication, project):
        """Create match records (more likely for recent papers)"""
        if random.random() > 0.3:  # 70% chance for match
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
            
            if random.random() > 0.4:  # 60% chance for match request
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

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    import django
    django.setup()
