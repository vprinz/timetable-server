import os

from celery.schedules import crontab

from .jsonenv import JsonEnv

env = JsonEnv('config.json')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lzqbf5&hc9r)pj8ge0-2a0spyefzy8(!-l7v#er168$9l4ij0d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEVELOPMENT = env['debug']
FIREBASE_API_KEY = env['firebase_api_key']
REDIS_HOST = env['redis_host']
LOG_DIR = os.path.join(BASE_DIR, '../logs/')

ADMINS = [('Valery Pavlikov', 'valerypavlikov@yandex.ru')]
ALLOWED_HOSTS = ['*']

# =============================== CORS =========================================

CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['sessionid']
CORS_ALLOW_HEADERS = default_headers = (
    'sessionid',
)

# =============================== END CORS =====================================

# =============================== EMAIL =====================================

if DEVELOPMENT:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_HOST = 'smtp.yandex.ru'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = env['email_host_user']
    EMAIL_HOST_PASSWORD = env['email_host_password']
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    EMAIL_USE_TLS = True
    SERVER_EMAIL = EMAIL_HOST_USER  # for logging

# =============================== END EMAIL =================================

# =============================== APPLICATION DEFINITION =======================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',

    'rest_framework',
    'rest_framework_swagger',

    'api',
    'users',
    'university',
]

# =============================== END APPLICATION DEFINITION ===================

# =============================== MIDDLEWARE ===================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'common.middleware.HeaderSessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.LoginRequiredMiddleware',
    'common.middleware.UpdateLastActivityMiddleware',
]

# =============================== END MIDDLEWARE ===============================

# =============================== LOGGING ======================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.errors'),
            'level': 'ERROR',
            'formatter': 'verbose',
        },
        'infofile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'django.information'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'errors': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'informator': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    },
}

if not DEVELOPMENT:
    LOGGING['handlers']['mail_admins'] = {
        'level': 'ERROR',
        'filters': [],
        'class': 'django.utils.log.AdminEmailHandler',
    }
    LOGGING['loggers']['errors'].update({'handlers': ['file', 'mail_admins']})
    LOGGING['loggers']['informator'].update({'handlers': ['infofile']})
    LOGGING['loggers']['django'] = {
        'handlers': ['file', 'mail_admins'],
        'level': 'DEBUG',
        'propagate': True
    }

# =============================== END LOGGING ==================================

# =============================== REST FRAMEWORK ===============================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'common.permissions.CsrfExemptSessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'common.utils.custom_exception_handler',
}

# =============================== END REST FRAMEWORK ===========================

# =============================== DEFAULT SETTINGS =============================

# =============================== CELERY =========================================

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379'
CELERY_BEAT_SCHEDULE = {
    'task-number-one': {
        'task': 'university.tasks.change_current_type_of_week',
        'schedule': crontab(minute=0, hour=18, day_of_week='sun'),
    },
}

# =============================== END CELERY =====================================

ROOT_URLCONF = 'timetable.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'timetable.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# =============================== END DEFAULT SETTINGS =========================

# =============================== DATABASES ====================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': env['database_host'],
        'NAME': env.get('database_name', 'timetable'),
        'PASSWORD': env.get('database_password', 'timetable'),
        'PORT': env.get('database_port', 5432),
        'USER': env.get('database_user', 'timetable'),
    }
}

# =============================== END DATABASES ================================

# =============================== PASSWORD VALIDATION ==========================

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

# =============================== END PASSWORD VALIDATION ======================

# =============================== INTERNATIONALIZATION =========================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

# =============================== END INTERNATIONALIZATION =====================

# =============================== STATIC FILES =================================

STATIC_ROOT = os.path.join(BASE_DIR, '../static/')  # for Nginx
STATIC_URL = '/static/'

# =============================== END STATIC FILES =============================
