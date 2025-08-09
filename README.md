# Research Publication Log System

A web-based platform for managing, tracking, and archiving research publications related to projects executed on the BA-HPC. The system streamlines follow-ups, automates archiving, and periodically harvests publications from selected sources, providing a centralized solution for researchers and administrators.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Roles & Permissions](#roles--permissions)
- [Development & Contribution](#development--contribution)
- [License](#license)

---

## Overview

The Research Publication Log System offers:
- Tracking of research publications tied to specific BA-HPC projects.
- Automated notifications for researchers regarding deadlines and missing information.
- Archiving of both publication URLs and PDF files.
- Periodic harvesting of publications from external sources.

**Target Users:**  
- Researchers working on BA-HPC projects  
- Project administrators and institutional managers

---

## Features

- **Automated Follow-up:** Email reminders as project deadlines approach to prompt researchers to log publications.
- **Archiving:** Auto-downloads PDFs for submitted publications; notifies researchers if PDF retrieval fails.
- **Harvesting:** Periodically crawls selected sources for new publications, matches entries to project metadata, and notifies researchers.
- **User Authentication:** Role-based access for researchers and admins.
- **Publication Upload:** Supports both URL and PDF submissions.
- **Admin Dashboard:** Manage users, projects, and publications.
- **Automated Notifications:** Reminds researchers about missing or incomplete records.

---

## Directory Structure

The main structure of the repository:

```
.
├── db.sqlite3
├── manage.py
├── requirements.txt
├── config/                 # Django project settings and configuration
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── media/
│   ├── publications/
│   │   └── files/          # Uploaded and auto-fetched PDF files
│   └── images/             # Uploaded/public images
├── projects/               # Main Django app
│   ├── admin.py
│   ├── apps.py
│   ├── email.py            # Email notifications logic
│   ├── forms.py
│   ├── models.py           # Project, Researcher, Publication models
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── AI/                 # AI/NLP models and logic
│   ├── management/
│   │   └── commands/       # Custom Django commands (e.g., seeding DB)
│   ├── migrations/
│   ├── static/             # App-specific static files (css, js, images)
│   └── templates/
│       ├── emails/         # Email templates (reminders, notifications)
│       ├── projects/       # Project-related UI templates
│       ├── Publications/   # Publication-related UI templates
│       └── registration/   # Auth & dashboard templates
└── staticfiles/            # Collected static files for deployment
```

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BasantAwad/Publication_Log.git
   cd Publication_Log
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the project:**
   - Edit `config/settings.py` for database, email, and harvesting settings.
   - Place any sensitive settings (e.g., credentials) in environment variables or a `.env` file.

5. **Apply migrations and create superuser:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

---

## Configuration

- **Database:** Configured in `config/settings.py` (default: SQLite)
- **Email Service:** Configure SMTP or other email settings in `settings.py`
- **Publication Sources:** Add domains/URIs for harvesting in your config
- **Media/Static Files:** Ensure `media/` and `staticfiles/` have correct permissions for uploads and serving

---

## Usage

- **Researchers:** Log in, add/update project-related publications, upload PDFs or provide URLs.
- **Admins:** Manage users, projects, review publications, trigger reminders, and oversee harvesting.
- **Automated Processes:** Reminders, archiving, and harvesting run as scheduled tasks or management commands.

---

## Roles & Permissions

- **Admin:** Full access to all users, projects, and publications.
- **Researcher:** Can only access and modify their own publications and projects.

---

## Development & Contribution

- To extend or contribute, use the structure above.
- Custom management commands live in `projects/management/commands/`.
- Templates for emails, UI, and dashboards are under `projects/templates/`.
- Static assets are in both `projects/static/` and project-wide `staticfiles/`.
- Follow standard Django best practices for feature or bugfix branches.

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

> For more details and the latest updates, visit the [GitHub repository](https://github.com/BasantAwad/Publication_Log).
