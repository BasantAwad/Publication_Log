# Realistic research data for database seeding

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
    "Columbia University"
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
    "Information Systems"
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
    "Apple Research"
]

# Real publication titles from actual research papers
REAL_PUBLICATION_TITLES = {
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
        "Sequence to Sequence Learning with Neural Networks"
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
        "Machine Learning: A Probabilistic Perspective"
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
        "The Art of Data Science: A Guide for Anyone Who Works with Data"
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
        "Cryptography: Theory and Practice"
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
        "Computer Vision: Detection, Recognition and Reconstruction"
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
        "Natural Language Processing: A Comprehensive Guide"
    ]
}

# Real research domains with actual descriptions
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
    }
}

# Real author names (famous researchers in the field)
FAMOUS_RESEARCHERS = [
    "Yann LeCun",
    "Geoffrey Hinton", 
    "Yoshua Bengio",
    "Andrew Ng",
    "Fei-Fei Li",
    "Jürgen Schmidhuber",
    "Ian Goodfellow",
    "Andrej Karpathy",
    "Sebastian Thrun",
    "Peter Norvig",
    "Stuart Russell",
    "Michael Jordan",
    "Christopher Bishop",
    "Trevor Hastie",
    "Robert Tibshirani",
    "Jerome Friedman",
    "Vladimir Vapnik",
    "Leslie Valiant",
    "Manuel Blum",
    "Richard Karp"
]

# Real abstract templates for different domains
ABSTRACT_TEMPLATES = {
    "Machine Learning": [
        "This paper presents a novel approach to {keyword1} that addresses the challenge of {keyword2} in machine learning. Our method leverages {keyword3} techniques to achieve significant improvements in {metric} compared to existing approaches. We evaluate our approach on benchmark datasets and demonstrate {percentage}% improvement in performance. The results show that our method is particularly effective for {keyword4} applications and opens new directions for future research in machine learning.",
        "We introduce a new {keyword1} framework that combines {keyword2} with {keyword3} to solve complex problems in machine learning. Our approach addresses the limitations of current {keyword4} methods by incorporating advanced optimization techniques. Experimental results on standard benchmarks show that our method achieves state-of-the-art performance with {percentage}% better results than existing techniques."
    ],
    "Artificial Intelligence": [
        "This research investigates the application of {keyword1} to enhance {keyword2} systems in artificial intelligence. We propose a novel {keyword3} algorithm that integrates {keyword4} with reasoning capabilities to improve decision-making. Our approach demonstrates superior performance in reasoning tasks compared to traditional methods, achieving {percentage}% improvement in accuracy.",
        "We present a comprehensive study of {keyword1} techniques applied to {keyword2} problems in artificial intelligence. Our work addresses the challenge of {keyword3} by developing innovative {keyword4} methods. The proposed approach combines theoretical insights with practical implementations, achieving {percentage}% better performance than existing solutions."
    ],
    "Data Science": [
        "This paper explores the application of {keyword1} methods to extract meaningful insights from {keyword2} datasets. We develop a novel {keyword3} approach that combines {keyword4} with statistical modeling to address the challenges of data quality and scalability. Our method demonstrates {percentage}% improvement in prediction accuracy compared to traditional approaches.",
        "We propose an innovative {keyword1} framework that leverages {keyword2} techniques to solve complex {keyword3} problems. Our approach addresses the limitations of existing methods by incorporating {keyword4} principles and advanced algorithms. Experimental evaluation demonstrates {percentage}% improvement in performance metrics."
    ]
}
