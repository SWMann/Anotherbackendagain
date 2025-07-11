import os
import sys
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and 'RENDER' not in os.environ and 'DIGITALOCEAN' not in os.environ:
    SECRET_KEY = 'django-insecure-key-for-dev-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
FRONTEND_URL = os.environ.get('FRONTEND_URL')

# URL prefix configuration for deployment
FORCE_SCRIPT_NAME = os.environ.get('FORCE_SCRIPT_NAME', '/anotherbackendagain-backend2')

# Get the ALLOWED_HOSTS from the environment variable
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1:8000').split(',')

# Add the Digital Ocean app's domain automatically
DO_APP_URL = os.environ.get('APP_URL')
if DO_APP_URL:
    ALLOWED_HOSTS.append(DO_APP_URL)
    ALLOWED_HOSTS.append(f'www.{DO_APP_URL}')

# Determine if we're running on Digital Ocean
ON_DIGITAL_OCEAN = os.environ.get('DIGITAL_OCEAN', 'False').lower() == 'true'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'social_django',
    'django_filters',
    'storages',  # For Digital Ocean Spaces (S3-compatible)

    # Local apps
    'apps.core',
    'apps.users',
    'apps.units',
    'apps.events',
    'apps.authentication',
    'apps.operations',
    'apps.training',
    'apps.ships',
    'apps.forums',
    'apps.standards',
    'apps.onboarding',
    'apps.announcements',
    'apps.vehicles',
]

# Update MIDDLEWARE to ensure WhiteNoise is in the correct position
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Right after SecurityMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# For development, you might also need to add this
if DEBUG:
    # This helps in development
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

# Security settings for production
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = False  # Keep this False since we're behind a proxy
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # Add proxy headers for Digital Ocean
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

ROOT_URLCONF = 'config.urls'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# Static files configuration with URL prefix
if FORCE_SCRIPT_NAME:
    STATIC_URL = f'{FORCE_SCRIPT_NAME}/static/'
else:
    STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration for URL prefix
WHITENOISE_STATIC_PREFIX = '/static/'

# Media files configuration with URL prefix
if FORCE_SCRIPT_NAME:
    MEDIA_URL = f'{FORCE_SCRIPT_NAME}/media/'
else:
    MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Use DATABASE_URL from environment if available (Digital Ocean provides this)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Local development database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 120,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('ACCESS_TOKEN_MINUTES', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('REFRESH_TOKEN_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Discord OAuth Settings
SOCIAL_AUTH_DISCORD_KEY = os.environ.get('DISCORD_CLIENT_ID', '')
SOCIAL_AUTH_DISCORD_SECRET = os.environ.get('DISCORD_CLIENT_SECRET', '')
SOCIAL_AUTH_DISCORD_SCOPE = ['identify', 'email', 'guilds']
SOCIAL_AUTH_DISCORD_REDIRECT_URI = os.environ.get('SOCIAL_AUTH_DISCORD_REDIRECT_URI', '')

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.discord.DiscordOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'apps.users.pipeline.get_discord_avatar',
)

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', "http://localhost:3000, https://discord.com").split(',')

# Add this to your settings.py file, replacing the existing storage configuration

# Digital Ocean Spaces (S3-compatible) settings
USE_SPACES = os.environ.get('USE_SPACES', 'False').lower() == 'true'

if USE_SPACES:
    # Digital Ocean Spaces settings
    AWS_ACCESS_KEY_ID = os.environ.get('SPACES_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('SPACES_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('SPACES_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('SPACES_REGION_NAME', 'nyc3')
    AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    AWS_LOCATION = 'static'
    AWS_QUERYSTRING_AUTH = False

    # Added CDN configuration
    USE_SPACES_CDN = os.environ.get('USE_SPACES_CDN', 'True').lower() == 'true'
    if USE_SPACES_CDN:
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.cdn.digitaloceanspaces.com'
    else:
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'

    # Django 4.2+ uses STORAGES dictionary
    STORAGES = {
        "default": {
            "BACKEND": "config.storage_backends.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
    }

    # Keep these for backwards compatibility with Django < 4.2
    DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # When using Spaces, media files are served directly from the CDN
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local file storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # Media files configuration with URL prefix
    if FORCE_SCRIPT_NAME:
        MEDIA_URL = f'{FORCE_SCRIPT_NAME}/media/'
    else:
        MEDIA_URL = '/media/'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Remove these duplicate lines at the bottom of your settings.py file:
# DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

