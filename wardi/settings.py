"""
Django settings for the Wardi project.

This file is configured to use python-decouple to manage sensitive settings
from a .env file in the project's root directory.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# It is loaded from the .env file in your project root.
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# The .env file should have DEBUG=False for production environments.
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = []


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Your project's apps
    'landing',
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

ROOT_URLCONF = 'wardi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Optional: A project-level templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wardi.wsgi.application'


# ==============================================================================
# DATABASE
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==============================================================================
# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================================
# INTERNATIONALIZATION
# https://docs.djangoproject.com/en/5.2/topics/i18n/
# ==============================================================================

LANGUAGE_CODE = 'id'  # Set to Indonesian

TIME_ZONE = 'Asia/Jakarta' # Set to your local time zone

USE_I18N = True

USE_TZ = True


# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# ==============================================================================

STATIC_URL = '/static/'

# Add this to tell Django where to find your project-level static files.
# Your 'landing' app's static files will be found automatically.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# AUTHENTICATION & REDIRECTS
# ==============================================================================

LOGIN_URL = 'login_page'
LOGIN_REDIRECT_URL = 'landing_page'
LOGOUT_REDIRECT_URL = 'landing_page'


# ==============================================================================
# THIRD-PARTY API KEYS
# ==============================================================================

# Load the Google AI API Key from the .env file
GOOGLE_AI_API_KEY = config('GOOGLE_AI_API_KEY', default='')
