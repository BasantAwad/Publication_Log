<p align="center">
  <img src="https://raw.githubusercontent.com/BasantAwad/BasantAwad/main/assets/basant-terminal-banner.png" alt="Terminal-inspired project banner" width="100%" />
</p>

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
