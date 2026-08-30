<p align="center"><img src="https://raw.githubusercontent.com/BasantAwad/BasantAwad/main/assets/introduction-banner.svg" alt="Terminal-inspired project banner" width="100%" /></p>

<!-- terminal-badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/NLP-8B5CF6?style=flat-square&logo=python&logoColor=white" alt="NLP" />
</p>

<p align="center"><img src="https://raw.githubusercontent.com/BasantAwad/BasantAwad/main/assets/introduction-banner.svg" alt="Animated terminal profile for Basant Awad Mohamed" width="100%" /></p>

# Publication Log Platform

A Django-based research-publication workflow for collecting, normalizing, searching, and archiving publication metadata. The project was designed around the Bibliotheca Alexandrina research-publication use case.

## Focus

The application supports metadata harvesting, publication records, search-oriented organization, and a maintainable backend structure suitable for research teams. It is a practical example of turning an administrative workflow into a searchable service.

## Stack

Python, Django, PostgreSQL, REST APIs, JWT authentication, NLP-assisted search, and rate limiting.

## Setup

Create a virtual environment, install the project requirements, configure PostgreSQL through environment variables, apply migrations, and start the Django development server. Check the project configuration and deployment notes before running it in a shared environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
