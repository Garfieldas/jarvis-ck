from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
BASE_URL = os.environ.get('BASE_URL')

import app, theme

THEME_APP_DIR = os.path.dirname(theme.__file__)
APP_DIR = os.path.dirname(app.__file__)

STATICFILES_DIRS = [
    os.path.join(THEME_APP_DIR, 'static'),
    os.path.join(APP_DIR, 'static_resources'),
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "tailwind",
    "theme",
    "app",
    "django_rq",
    "django_select2",
]

AUTH_USER_MODEL = 'app.User'

if DEBUG:
    
    INSTALLED_APPS += ["django_browser_reload"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.RestrictAdminMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:

    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', APP_DIR + '/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'page_tags': 'app.template_tags.page_tags',
            },
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

POSTGRES_DB = os.environ.get('POSTGRES_DB', os.environ.get('POSTGRESS_DB', ''))
POSTGRES_USER = os.environ.get('POSTGRES_USER', os.environ.get('POSTGRESS_USER', ''))
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', os.environ.get('POSTGRESS_PASSWORD', ''))
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', os.environ.get('POSTGRESS_HOST', 'localhost'))
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', os.environ.get('POSTGRESS_PORT', '5432'))

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': POSTGRES_DB,
            'USER': POSTGRES_USER,
            'PASSWORD': POSTGRES_PASSWORD,
            'HOST': POSTGRES_HOST,
            'PORT': POSTGRES_PORT,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Vilnius'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TAILWIND_APP_NAME = "theme"


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

rq_default_queue = {
    'HOST': REDIS_HOST,
    'PORT': int(REDIS_PORT),
    'DB': 4,
    'DEFAULT_TIMEOUT': 360,
}

if REDIS_PASSWORD:
    rq_default_queue['PASSWORD'] = REDIS_PASSWORD

RQ_QUEUES = {
    'default': rq_default_queue,
}

REDIS_AUTH = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""

REDIS_URL = f"redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/0"
SELECT_2_REDIS_URL = f"redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/1"
RQ_REDIS_URL = f"redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/2"

CACHES = {
    'default': {
        'BACKEND': "django_redis.cache.RedisCache",
        'LOCATION': REDIS_URL,
    },
    "select2": {
        'BACKEND': 'django_redis.cache.RedisCache',
        "LOCATION": SELECT_2_REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "rq_cache": {
        'BACKEND': 'django_redis.cache.RedisCache',
        "LOCATION": RQ_REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cache-for-ratelimiting": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ratelimit-cache"
    },
}

# Ratelimit
RATELIMIT_USE_CACHE = 'cache-for-ratelimiting'
RATELIMIT_VIEW = 'app.views.auth.ratelimited'

# Select2
SELECT2_CACHE_BACKEND = "select2"

# Auth redirects
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
