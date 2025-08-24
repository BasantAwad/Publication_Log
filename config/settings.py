from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# Base Directory
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Security & Debug
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default")  # ضع SECRET_KEY في .env
DEBUG = True  # غيّرها False للإنتاج
ALLOWED_HOSTS = []

# =========================
# RAG & LLM Settings
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
RAG_INDEX_DIR = os.getenv("RAG_INDEX_DIR", str(BASE_DIR / "projects" / "AI" / "rag_index"))
RAG_EMB_MODEL = os.getenv("RAG_EMB_MODEL", "intfloat/e5-base")
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", 1500))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", 150))
RAG_SCOPE = os.getenv("RAG_SCOPE", "publication_log")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # 'ollama' | 'openai' | 'custom'
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

SITE_URL = "http://127.0.0.1:8000"

# =========================
# Applications
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'projects',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'projects' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# =========================
# Database
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =========================
# Password Validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =========================
# Internationalization
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================
# Static & Media Files
# =========================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =========================
# Defaults
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/user_dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
