import os
import random
import string
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool
from .logger import LOGGING as is_LOGGING
from urllib.parse import urlparse
import importlib

# =========================== MAIN CONFIGS ===========================

load_dotenv()  # take environment variables from .env.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Enable/Disable DEBUG Mode
DEBUG = str2bool(os.environ.get('DEBUG'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choices(
        string.ascii_letters + string.digits, k=32))

ROOT_URLCONF = "core.urls"
AUTH_USER_MODEL = 'home.User'
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = '/'

# =========================== LOOGER CONFIGS ===========================

LOGGING = is_LOGGING

# =========================== CORS CONFIGS ===========================

ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'http://localhost', 'http://192.168.15.4:6085', 'http://127.0.0.1:6085', 'http://localhost:6085',]
X_FRAME_OPTIONS = "SAMEORIGIN"

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and not DEBUG:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

RENDER_EXTERNAL_FRONTEND = os.environ.get('RENDER_EXTERNAL_FRONTEND')
if RENDER_EXTERNAL_FRONTEND and not DEBUG:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_FRONTEND}')

# =========================== INSTALLED APPS CONFIGS ===========================

INSTALLED_APPS = [

    "admin_volt.apps.AdminVoltConfig",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "serve_files",
    "auditlog",

    "home",
    "notification",
    "import_export",
    "corsheaders",
    "auditor",
]

# =========================== MIDDLEWARE CONFIGS ===========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "auditor.middleware.AuditorMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "middlewares.access_apps.LoginRequiredAccess",
    "middlewares.forbidden_redirect_middleware.ForbiddenRedirectMiddleware",
    "middlewares.rate_limit_api_external.RateLimitMiddleware",
]

# =========================== TEMPLATES CONFIGS ===========================

HOME_TEMPLATES = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =========================== DATABASE CONFIGS ===========================

DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
DB_USERNAME = os.getenv('DB_USERNAME' , None)
DB_PASS     = os.getenv('DB_PASS'     , None)
DB_HOST     = os.getenv('DB_HOST'     , None)
DB_PORT     = os.getenv('DB_PORT'     , None)
DB_NAME     = os.getenv('DB_NAME'     , None)

if DB_ENGINE and DB_NAME and DB_USERNAME:
    DATABASES = {
      'default': {
        'ENGINE'  : 'django.db.backends.' + DB_ENGINE,
        'NAME'    : DB_NAME,
        'USER'    : DB_USERNAME,
        'PASSWORD': DB_PASS,
        'HOST'    : DB_HOST,
        'PORT'    : DB_PORT,
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
    
# =========================== PASSWORD VALIDATION CONFIGS ===========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =========================== INTERNATIONALIZATION CONFIGS ===========================

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Recife"
USE_I18N = True
USE_TZ = True
DECIMAL_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = True
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i:s'

# =========================== STATIC FILES CONFIGS ===========================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Defina a URL base para os arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# =========================== EMAIL CONFIGS ===========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CONFIG_EMAIL_ENABLE = os.getenv('CONFIG_EMAIL_ENABLE', False)
if CONFIG_EMAIL_ENABLE:
    EMAIL_USE_TLS = os.getenv('CONFIG_EMAIL_USE_TLS')
    EMAIL_HOST = os.getenv('CONFIG_EMAIL_HOST')
    EMAIL_HOST_USER = os.getenv('CONFIG_EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('CONFIG_EMAIL_HOST_PASSWORD')
    EMAIL_PORT = os.getenv('CONFIG_EMAIL_PORT')
    DEFAULT_FROM_EMAIL = os.getenv('CONFIG_DEFAULT_FROM_EMAIL')

# =========================== CACHES CONFIGS ===========================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache' if not DEBUG else 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.getenv('DJANGO_CACHE_REDIS_URI') if not DEBUG else 'unique-snowflake',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_TIMEOUT': 5,  # Ajuste conforme necessário
            'KEY_PREFIX': 'suop',  # Prefixo opcional para suas chaves
        } if not DEBUG else {}
    }
}

# =========================== SECURITY CONFIG ===========================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =========================== ENCRYPTION CONFIG ===========================

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE'))
SERVE_DECRYPTED_FILE_URL_BASE = os.environ.get('SERVE_DECRYPTED_FILE_URL_BASE')

# =========================== AUDITOR CONFIGS ===========================

AUDITOR_MIDDLEWARE_ENABLE = os.getenv('CONFIG_AUDITOR_MIDDLEWARE_ENABLE', False)
AUDITOR_MIDDLEWARE_RESTRICT_PATHS = ["/api/", "/app/", "/admin/"]

# =========================== EXTRA CONFIGS ===========================

SEND_EMAIL_DEGUB = os.getenv('SEND_EMAIL_DEGUB', False)
