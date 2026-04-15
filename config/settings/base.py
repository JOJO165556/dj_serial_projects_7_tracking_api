from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


SECRET_KEY = os.getenv("SECRET_KEY")

# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'apps.users',
    'apps.couriers',
    'apps.parcels',
    'apps.tracking',
    'apps.realtime',
    'apps.dashboard',
    'apps.analytics',
    'apps.notifications',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS":
"drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Tracking API",
    "DESCRIPTION": "Logistics tracking system",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"BearerAuth": []}],
}

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = "users.User"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

db_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
DATABASES = {
    'default': dj_database_url.parse(
        db_url,
        conn_max_age=600
    )
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("Français")),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
