import os
import random
import datetime
import requests
from faker import Faker
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from projects.models import Project, Author, Publication, HarvestMatchCandidate, MatchRequest, UserProfile
from django.contrib.auth.models import User

# Import realistic data
from realistic_data import (
    ACADEMIC_INSTITUTIONS, DEPARTMENTS, FUNDING_SOURCES, 
    REAL_PUBLICATION_TITLES, RESEARCH_DOMAINS, FAMOUS_RESEARCHERS,
    ABSTRACT_TEMPLATES
)

fake = Faker()

# Real research domains with actual descriptions and keywords
RESEARCH_DOMAINS = {
    "Machine Learning": {
        "description": "Advancing algorithms and models that enable computers to learn from data without being explicitly programmed",
        "keywords": ["deep learning", "neural networks", "computer vision", "natural language processing", "reinforcement learning", "transfer learning", "supervised learning", "unsupervised learning"]
    },
    "Artificial Intelligence": {
        "description": "Developing intelligent systems that can perform tasks requiring human intelligence, including reasoning, learning, and problem-solving",
        "keywords": ["expert systems", "knowledge representation", "automated reasoning", "planning", "machine learning", "natural language understanding", "computer vision", "robotics"]
    },
    "Data Science": {
        "description": "Extracting insights and knowledge from structured and unstructured data using scientific methods, algorithms, and systems",
        "keywords": ["statistics", "data mining", "predictive analytics", "big data", "data visualization", "statistical modeling", "business intelligence", "data engineering"]
    },
    "Cybersecurity": {
        "description": "Protecting systems, networks, and programs from digital attacks, damage, or unauthorized access",
        "keywords": ["cryptography", "network security", "penetration testing", "threat intelligence", "incident response", "security architecture", "vulnerability assessment", "digital forensics"]
    },
    "Computer Vision": {
        "description": "Enabling computers to interpret and understand visual information from the world, including images and videos",
        "keywords": ["image processing", "object detection", "facial recognition", "medical imaging", "autonomous vehicles", "augmented reality", "pattern recognition", "image segmentation"]
    },
    "Natural Language Processing": {
        "description": "Enabling computers to understand, interpret, and generate human language in a meaningful way",
        "keywords": ["text analysis", "sentiment analysis", "machine translation", "question answering", "text summarization", "named entity recognition", "language modeling", "speech recognition"]
    },
    "Quantum Computing": {
        "description": "Developing computing systems that leverage quantum mechanical phenomena to process information",
        "keywords": ["quantum algorithms", "quantum cryptography", "quantum machine learning", "quantum simulation", "quantum error correction", "quantum gates", "quantum entanglement", "quantum supremacy"]
    },
    "Blockchain Technology": {
        "description": "Creating decentralized, distributed ledgers that record transactions across multiple computers securely",
        "keywords": ["distributed systems", "cryptography", "smart contracts", "consensus algorithms", "decentralized applications", "cryptocurrency", "digital identity", "supply chain"]
    },
    "Internet of Things (IoT)": {
        "description": "Connecting physical devices and objects to the internet to collect and exchange data",
        "keywords": ["sensor networks", "edge computing", "wireless communication", "embedded systems", "smart cities", "industrial IoT", "wearable technology", "home automation"]
    },
    "Cloud Computing": {
        "description": "Providing computing services over the internet, including servers, storage, databases, and software",
        "keywords": ["distributed systems", "virtualization", "microservices", "containerization", "serverless computing", "cloud security", "scalability", "high availability"]
    }
}

# Real publication titles from actual research papers
PUBLICATION_TITLES = {
    "Machine Learning": [
        "Attention Is All You Need",
        "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "Deep Residual Learning for Image Recognition",
        "Generative Adversarial Networks",
        "Long Short-Term Memory",
        "Convolutional Neural Networks for Visual Recognition",
        "Reinforcement Learning: An Introduction",
        "Transfer Learning in Deep Neural Networks",
        "ImageNet Classification with Deep Convolutional Neural Networks",
        "Sequence to Sequence Learning with Neural Networks",
        "Word2Vec: Efficient Estimation of Word Representations in Vector Space",
        "Gradient-Based Learning Applied to Document Recognition",
        "Dropout: A Simple Way to Prevent Neural Networks from Overfitting",
        "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift",
        "Adam: A Method for Stochastic Optimization"
    ],
    "Artificial Intelligence": [
        "A Survey of Artificial General Intelligence",
        "Knowledge Representation and Reasoning",
        "Planning and Acting in Partially Observable Domains",
        "Multi-Agent Systems: Algorithmic, Game-Theoretic, and Logical Foundations",
        "Probabilistic Graphical Models: Principles and Techniques",
        "Automated Planning: Theory and Practice",
        "Intelligent Agents: Theory and Practice",
        "Artificial Intelligence: A Modern Approach",
        "The Quest for Artificial Intelligence: A History of Ideas and Achievements",
        "Machine Learning: A Probabilistic Perspective",
        "Pattern Recognition and Machine Learning",
        "The Elements of Statistical Learning: Data Mining, Inference, and Prediction",
        "Reinforcement Learning: An Introduction",
        "Deep Learning",
        "Neural Networks and Deep Learning: A Textbook"
    ],
    "Data Science": [
        "The Elements of Statistical Learning: Data Mining, Inference, and Prediction",
        "Data Mining: Concepts and Techniques",
        "Predictive Analytics: The Power to Predict Who Will Click, Buy, Lie, or Die",
        "Big Data: A Revolution That Will Transform How We Live, Work, and Think",
        "Data Science for Business: What You Need to Know about Data Mining and Data-Analytic Thinking",
        "Python for Data Analysis: Data Wrangling with Pandas, NumPy, and IPython",
        "R for Data Science: Import, Tidy, Transform, Visualize, and Model Data",
        "Introduction to Data Science: A Python Approach to Concepts, Techniques and Applications",
        "Data Science from Scratch: First Principles with Python",
        "The Art of Data Science: A Guide for Anyone Who Works with Data",
        "Data Mining: Practical Machine Learning Tools and Techniques",
        "Statistical Learning with Sparsity: The Lasso and Generalizations",
        "Applied Predictive Modeling",
        "Feature Engineering for Machine Learning: Principles and Techniques for Data Scientists",
        "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow"
    ],
    "Cybersecurity": [
        "Applied Cryptography: Protocols, Algorithms, and Source Code in C",
        "Network Security: Private Communication in a Public World",
        "The Art of Deception: Controlling the Human Element of Security",
        "Hacking: The Art of Exploitation",
        "Security Engineering: A Guide to Building Dependable Distributed Systems",
        "Cryptography and Network Security: Principles and Practice",
        "Computer Security: Principles and Practice",
        "Information Security: Principles and Practice",
        "Network Security Essentials: Applications and Standards",
        "Cryptography: Theory and Practice",
        "The Code Book: The Science of Secrecy from Ancient Egypt to Quantum Cryptography",
        "Security in Computing",
        "Introduction to Computer Security",
        "Computer Security: Art and Science",
        "Network Security: Principles and Practices"
    ],
    "Computer Vision": [
        "Computer Vision: Algorithms and Applications",
        "Learning OpenCV: Computer Vision with the OpenCV Library",
        "Multiple View Geometry in Computer Vision",
        "Computer Vision: A Modern Approach",
        "Feature Extraction and Image Processing for Computer Vision",
        "Computer Vision: Principles, Algorithms, Applications, Learning",
        "Digital Image Processing",
        "Computer Vision: Models, Learning, and Inference",
        "Computer Vision: From 3D Reconstruction to Recognition",
        "Computer Vision: Detection, Recognition and Reconstruction",
        "Computer Vision: A Reference Guide",
        "Computer Vision: Theory and Applications",
        "Computer Vision: Statistical Models for Image Interpretation",
        "Computer Vision: Analysis of Images and Videos",
        "Computer Vision: From Surfaces to 3D Objects"
    ],
    "Natural Language Processing": [
        "Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition",
        "Foundations of Statistical Natural Language Processing",
        "Natural Language Processing with Python: Analyzing Text with the Natural Language Toolkit",
        "Introduction to Information Retrieval",
        "Statistical Machine Translation",
        "Natural Language Understanding",
        "Natural Language Processing: A Machine Learning Perspective",
        "Natural Language Processing: From Theory to Practice",
        "Natural Language Processing: An Introduction",
        "Natural Language Processing: A Comprehensive Guide",
        "Natural Language Processing: Concepts, Methodologies, Tools, and Applications",
        "Natural Language Processing: A Survey",
        "Natural Language Processing: State of the Art and Future Directions",
        "Natural Language Processing: Techniques and Applications",
        "Natural Language Processing: Building Intelligent Systems"
    ],
    "Quantum Computing": [
        "Quantum Computation and Quantum Information",
        "Quantum Computing: A Gentle Introduction",
        "Quantum Computing for Computer Scientists",
        "Quantum Computing: An Applied Approach",
        "Quantum Computing: From Linear Algebra to Physical Realizations",
        "Quantum Computing: Progress and Prospects",
        "Quantum Computing: A Survey",
        "Quantum Computing: Principles and Applications",
        "Quantum Computing: Algorithms and Applications",
        "Quantum Computing: A Modern Approach",
        "Quantum Computing: Fundamentals and Applications",
        "Quantum Computing: Theory and Practice",
        "Quantum Computing: A Comprehensive Guide",
        "Quantum Computing: From Theory to Implementation",
        "Quantum Computing: Concepts and Applications"
    ],
    "Blockchain Technology": [
        "Mastering Bitcoin: Programming the Open Blockchain",
        "Mastering Ethereum: Building Smart Contracts and DApps",
        "Blockchain: Blueprint for a New Economy",
        "The Business Blockchain: Promise, Practice, and Application of the Next Internet Technology",
        "Blockchain Revolution: How the Technology Behind Bitcoin Is Changing Money, Business, and the World",
        "Blockchain: A Practical Guide to Developing Business, Law, and Technology Solutions",
        "Blockchain and the Law: The Rule of Code",
        "Blockchain: From Concept to Implementation",
        "Blockchain: A Comprehensive Guide",
        "Blockchain: Principles and Applications",
        "Blockchain: Technology and Applications",
        "Blockchain: A Survey",
        "Blockchain: Fundamentals and Applications",
        "Blockchain: Theory and Practice",
        "Blockchain: Concepts and Applications"
    ],
    "Internet of Things (IoT)": [
        "Internet of Things: A Hands-On Approach",
        "Building the Internet of Things: Implement New Business Models, Disrupt Competitors, Transform Your Industry",
        "Internet of Things: Principles and Paradigms",
        "Internet of Things: Architectures, Protocols, and Standards",
        "Internet of Things: From Theory to Practice",
        "Internet of Things: A Comprehensive Guide",
        "Internet of Things: Concepts and Applications",
        "Internet of Things: Technology and Applications",
        "Internet of Things: A Survey",
        "Internet of Things: Fundamentals and Applications",
        "Internet of Things: Theory and Practice",
        "Internet of Things: Principles and Applications",
        "Internet of Things: Concepts and Implementations",
        "Internet of Things: A Modern Approach",
        "Internet of Things: From Theory to Implementation"
    ],
    "Cloud Computing": [
        "Cloud Computing: Concepts, Technology & Architecture",
        "Cloud Computing: Principles and Paradigms",
        "Cloud Computing: A Practical Approach",
        "Cloud Computing: Theory and Practice",
        "Cloud Computing: Concepts and Applications",
        "Cloud Computing: A Comprehensive Guide",
        "Cloud Computing: Principles and Applications",
        "Cloud Computing: Technology and Applications",
        "Cloud Computing: A Survey",
        "Cloud Computing: Fundamentals and Applications",
        "Cloud Computing: Theory and Practice",
        "Cloud Computing: Principles and Applications",
        "Cloud Computing: Concepts and Implementations",
        "Cloud Computing: A Modern Approach",
        "Cloud Computing: From Theory to Implementation"
    ]
}

# Real academic institutions
ACADEMIC_INSTITUTIONS = [
    "Massachusetts Institute of Technology (MIT)",
    "Stanford University",
    "Harvard University",
    "University of California, Berkeley",
    "Carnegie Mellon University",
    "Princeton University",
    "University of Oxford",
    "University of Cambridge",
    "ETH Zurich",
    "EPFL (École Polytechnique Fédérale de Lausanne)",
    "Technical University of Munich",
    "University of Toronto",
    "University of British Columbia",
    "University of Washington",
    "University of Illinois at Urbana-Champaign",
    "Georgia Institute of Technology",
    "University of Michigan",
    "Cornell University",
    "University of Pennsylvania",
    "Columbia University",
    "Yale University",
    "University of Chicago",
    "University of California, Los Angeles",
    "University of California, San Diego",
    "University of Texas at Austin",
    "University of Wisconsin-Madison",
    "University of Maryland",
    "University of Southern California",
    "New York University",
    "University of California, Irvine"
]

# Real research departments
DEPARTMENTS = [
    "Computer Science",
    "Electrical Engineering and Computer Science",
    "Information Technology",
    "Data Science",
    "Artificial Intelligence",
    "Machine Learning",
    "Cybersecurity",
    "Computer Engineering",
    "Software Engineering",
    "Information Systems",
    "Computational Science",
    "Applied Mathematics",
    "Statistics",
    "Operations Research",
    "Bioinformatics",
    "Robotics",
    "Computer Vision",
    "Natural Language Processing",
    "Quantum Computing",
    "Blockchain Technology"
]

# Real funding sources
FUNDING_SOURCES = [
    "National Science Foundation (NSF)",
    "European Research Council (ERC)",
    "DARPA (Defense Advanced Research Projects Agency)",
    "Google Research",
    "Microsoft Research",
    "IBM Research",
    "Intel Research",
    "Amazon Research",
    "Facebook Research",
    "Apple Research",
    "OpenAI",
    "DeepMind",
    "National Institutes of Health (NIH)",
    "Department of Energy (DOE)",
    "Department of Defense (DoD)",
    "European Commission",
    "UK Research and Innovation",
    "Canadian Institutes of Health Research",
    "Australian Research Council",
    "Japan Science and Technology Agency"
]

class Command(BaseCommand):
    help = 'Seed database with realistic research data using actual publication titles and real research domains'

    def add_arguments(self, parser):
        parser.add_argument(
            '--authors',
            type=int,
            default=100,
            help='Number of authors to create (default: 100)'
        )
        parser.add_argument(
            '--publications-per-domain',
            type=int,
            default=10,
            help='Number of publications per domain (default: 10)'
        )
        parser.add_argument(
            '--send-emails',
            action='store_true',
            help='Send welcome emails to created authors'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting realistic database seeding...")
        os.environ["SEEDING"] = "true"
        
        # Create authors with realistic profiles
        authors = self.seed_authors(options['authors'])
        
        # Create domain projects with real research data
        projects = self.seed_domain_projects()
        
        # Create publications with actual titles
        publications = self.seed_publications(projects, authors, options['publications_per_domain'])
        
        # Create AI matching candidates
        self.seed_ai_matches(publications, projects)
        
        # Send welcome emails if requested
        if options['send_emails']:
            self.send_welcome_emails(authors)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database successfully seeded with {len(authors)} authors, '
                f'{len(projects)} projects, and {len(publications)} publications!'
            )
        )

    def generate_realistic_abstract(self, domain, title):
        """Generate a realistic abstract based on the actual publication title and domain"""
        keywords = RESEARCH_DOMAINS[domain]["keywords"]
        
        # Use imported realistic abstract templates
        if domain in ABSTRACT_TEMPLATES:
            template = random.choice(ABSTRACT_TEMPLATES[domain])
            return template.format(
                keyword1=random.choice(keywords),
                keyword2=random.choice(keywords),
                keyword3=random.choice(keywords),
                keyword4=random.choice(keywords),
                metric=random.choice(['accuracy', 'efficiency', 'scalability', 'robustness', 'performance']),
                percentage=random.randint(15, 75)
            )
        else:
            # Fallback to general template
            return f"This research addresses critical challenges in {domain.lower()} through the application of {random.choice(keywords)} and {random.choice(keywords)} techniques. We propose a novel approach that combines {random.choice(keywords)} with {random.choice(keywords)} to achieve significant improvements in {random.choice(['performance', 'efficiency', 'accuracy', 'scalability'])}. Our method demonstrates {random.randint(20, 70)}% better results compared to existing approaches and shows promising applications in real-world {domain.lower()} scenarios. The findings contribute to the advancement of {domain.lower()} and provide a foundation for future research in this field."

    def seed_authors(self, num_authors):
        """Create authors with realistic academic profiles"""
        self.stdout.write(f"Creating {num_authors} authors with realistic academic profiles...")
        
        authors = []
        for i in range(num_authors):
            # Use famous researchers for some authors, generate realistic names for others
            if i < len(FAMOUS_RESEARCHERS) and random.random() < 0.3:  # 30% chance to use famous researcher
                full_name = FAMOUS_RESEARCHERS[i]
                first_name, last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')
            else:
                first_name = fake.first_name()
                last_name = fake.last_name()
                full_name = f"{first_name} {last_name}"
            
            # Generate realistic academic email
            email_patterns = [
                f"{first_name[0].lower()}{last_name.lower()}@{random.choice([inst.split('(')[0].strip().lower().replace(' ', '').replace(',', '').replace('.', '') for inst in ACADEMIC_INSTITUTIONS[:10]])}.edu",
                f"{first_name.lower()}.{last_name.lower()}@{random.choice([inst.split('(')[0].strip().lower().replace(' ', '').replace(',', '').replace('.', '') for inst in ACADEMIC_INSTITUTIONS[10:20]])}.edu",
                f"{first_name.lower()}{last_name[0].lower()}@{random.choice([inst.split('(')[0].strip().lower().replace(' ', '').replace(',', '').replace('.', '') for inst in ACADEMIC_INSTITUTIONS[20:]])}.edu"
            ]
            email = random.choice(email_patterns)
            
            # Select research interests based on domains
            domain_choices = list(RESEARCH_DOMAINS.keys())
            selected_domains = random.sample(domain_choices, random.randint(1, 3))
            research_interests = []
            for domain in selected_domains:
                keywords = RESEARCH_DOMAINS[domain]["keywords"]
                research_interests.extend(random.sample(keywords, random.randint(2, 4)))
            
            # Create realistic author profile
            author = Author.objects.create(
                name=full_name,
                email=email,
                research_interests=", ".join(research_interests),
                institution=random.choice(ACADEMIC_INSTITUTIONS),
                department=random.choice(DEPARTMENTS),
                orcid_id=f"0000-000{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100, 999)}",
                email_notifications=random.choice([True, True, True, False])  # 75% want notifications
            )
            authors.append(author)
            
            if (i+1) % 20 == 0:
                self.stdout.write(f"Created {i+1} authors...")
        
        return authors

    def seed_domain_projects(self):
        """Create realistic research projects for each domain"""
        self.stdout.write("Creating realistic research domain projects...")
        
        projects = []
        for domain, details in RESEARCH_DOMAINS.items():
            # Create realistic project title
            project_titles = [
                f"Advanced {domain} Research Initiative",
                f"Cutting-Edge {domain} Development Project",
                f"Next-Generation {domain} Technologies",
                f"Innovative {domain} Solutions",
                f"State-of-the-Art {domain} Research"
            ]
            
            start_date = fake.date_between(
                start_date=datetime.date(2018, 1, 1),
                end_date='today'
            )
            duration_years = random.randint(2, 5)
            
            # Create realistic project
            project = Project.objects.create(
                title=random.choice(project_titles),
                created=start_date,
                team=f"{domain} Research Consortium",
                abstract=details["description"],
                duration=f"{duration_years} years",
                domain=domain,
                scientific_case=(
                    f"This project coordinates cutting-edge research efforts in {domain.lower()}, "
                    f"focusing on: {', '.join(details['keywords'][:4])}. Our consortium brings together "
                    f"experts from academia and industry to advance this critical field through "
                    f"collaborative research, shared resources, and innovative methodologies. "
                    f"The project aims to develop novel approaches to {random.choice(details['keywords'])} "
                    f"and establish new standards in {domain.lower()} research and applications."
                ),
                keywords=", ".join(details["keywords"]),
                status=random.choice(['active', 'active', 'active', 'completed']),
                principal_investigator=fake.name(),
                funding_source=random.choice(FUNDING_SOURCES),
                website=f"https://{domain.lower().replace(' ', '').replace('(', '').replace(')', '')}.research.edu"
            )
            projects.append(project)
            self.stdout.write(f"Created project: {project.title}")
        
        return projects

    def seed_publications(self, projects, authors, publications_per_domain):
        """Create publications with actual research titles"""
        self.stdout.write("Creating publications with real research titles...")
        
        publications = []
        for project in projects:
            domain = project.domain
            titles = REAL_PUBLICATION_TITLES.get(domain, [f"Research in {domain}"])
            
            # Use actual publication titles
            selected_titles = random.sample(titles, min(publications_per_domain, len(titles)))
            
            for title in selected_titles:
                # Create realistic publication year
                pub_year = project.created.year + random.randint(0, min(4, datetime.date.today().year - project.created.year))
                
                # Select primary author
                primary_author = random.choice(authors)
                
                # Create publication with real title
                publication = Publication.objects.create(
                    project=project,
                    title=title,
                    primary_author=primary_author,
                    abstract=self.generate_realistic_abstract(domain, title),
                    year=pub_year,
                    url=f"https://doi.org/{random.randint(10,99)}.{random.randint(1000,9999)}/{random.randint(100000,999999)}",
                    type=random.choice(["Journal", "Conference", "Preprint", "Workshop", "Book Chapter"]),
                    email_sent=False,
                    ai_processed=False
                )
                
                # Add realistic collaborators
                available_authors = [a for a in authors if a != primary_author]
                if available_authors:
                    num_collaborators = random.randint(1, min(4, len(available_authors)))
                    collaborators = random.sample(available_authors, num_collaborators)
                    publication.collaborators.add(*collaborators)
                
                publications.append(publication)
                
                self.stdout.write(f"Created publication: {title[:50]}... by {primary_author.name}")
        
        return publications

    def seed_ai_matches(self, publications, projects):
        """Create realistic AI matching candidates"""
        self.stdout.write("Creating realistic AI matching candidates...")
        
        for publication in publications:
            # 70% chance to create a match candidate
            if random.random() > 0.3:
                # Calculate realistic confidence based on domain match and keywords
                domain_match = publication.project.domain
                author_interests = publication.primary_author.get_research_interests_list()
                project_keywords = publication.project.get_keywords_list()
                
                # Higher confidence if author interests match project keywords
                base_confidence = 0.65
                if any(interest in project_keywords for interest in author_interests):
                    base_confidence += 0.25
                
                confidence = min(0.95, base_confidence + random.uniform(0, 0.15))
                
            HarvestMatchCandidate.objects.create(
                publication=publication,
                    project=publication.project,
                matched_by_ai=True,
                    confidence_score=confidence,
                created_at=fake.date_time_between(
                    start_date=datetime.datetime(publication.year, 1, 1),
                    end_date='now'
                )
            )
                
                # Update publication AI status
                publication.ai_processed = True
                publication.ai_confidence = confidence
                publication.save()
                
                # 60% chance to create a match request
                if random.random() > 0.4:
                    shared_authors = list(publication.collaborators.all())[:2]
                    if shared_authors:
                MatchRequest.objects.create(
                            project=publication.project,
                    publication=publication,
                    match_title=publication.title,
                            match_score=confidence,
                    match_authors=", ".join(a.name for a in shared_authors),
                    approved=random.choice([True, False, None])
                )

    def send_welcome_emails(self, authors):
        """Send realistic welcome emails to authors"""
        self.stdout.write("Sending realistic welcome emails to authors...")
        
        for author in authors:
            if author.email_notifications:
                try:
                    send_mail(
                        subject='Welcome to the Research Publication Platform',
                        message=f"""
Dear {author.name},

Welcome to our research publication platform! We're excited to have you join our community of researchers.

Your profile has been created with the following details:
- Name: {author.name}
- Email: {author.email}
- Institution: {author.institution}
- Department: {author.department}
- Research Interests: {author.research_interests}

You can now:
- Browse publications in your research areas
- Connect with other researchers in your field
- Submit your own publications
- Receive AI-powered publication recommendations
- Access research collaboration tools

We look forward to seeing your contributions to the research community!

Best regards,
The Research Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[author.email],
                        fail_silently=True
                    )
                    
                    # Mark email as sent
                    author_pubs = Publication.objects.filter(primary_author=author)
                    author_pubs.update(email_sent=True)
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to send email to {author.email}: {e}")
                    )

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()