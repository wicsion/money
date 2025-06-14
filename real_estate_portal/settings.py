import sys
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-ваш-резервный-ключ-для-разработки')

DEBUG = True
handler500 = 'accounts.views.server_error'
ALLOWED_HOSTS = ['winwindeal.up.railway.app' ]


CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'https://winwindeal.up.railway.app'
]


INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'brokers.apps.BrokersConfig',
    'developers.apps.DevelopersConfig',
    'clients.apps.ClientsConfig',
    'properties.apps.PropertiesConfig',
    'payments.apps.PaymentsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'widget_tweaks',
    'channels',
    'corsheaders',
    'django.contrib.humanize',




]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.ActivityLoggerMiddleware',
    'accounts.middleware.ProfileCompletionMiddleware',
    'corsheaders.middleware.CorsMiddleware',

]

ROOT_URLCONF = 'real_estate_portal.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'accounts.context_processors.subscriptions',
            ],
        },
    },
]
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

WSGI_APPLICATION = 'real_estate_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'kegZgPeddbHDLCNATEgJZWFRxAncDvBj',
        'HOST': 'tramway.proxy.rlwy.net',
        'PORT': '30529',

        }
    }


# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'accounts.backends.EmailVerifiedBackend',
]

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_MAX_MEMORY_SIZE = 10*1024*1024

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
WHITENOISE_MAX_AGE = 86400
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Настройки Whitenoise для статических файлов
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

AUTH_USER_MODEL = 'accounts.User'

CORS_ALLOWED_ORIGINS = ['https://winwindeal.up.railway.app']
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

#AWS_S3_SIGNATURE_VERSION = 's3v4'
#AWS_DEFAULT_ACL = 'public-read'
#AWS_QUERYSTRING_AUTH = False
#AWS_S3_OBJECT_PARAMETERS = {
    #'CacheControl': 'max-age=86400',
#}

#if DEBUG:
    #DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    # Убедитесь, что MEDIA_ROOT и MEDIA_URL настроены
   # MEDIA_URL = '/media/'
    #MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#else:
    #DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Настройки S3 (оставьте ваши текущие AWS-ключи и endpoint)
    #AWS_ACCESS_KEY_ID = '95bf86962b9e4d1d94958be095e5d901'
   # AWS_SECRET_ACCESS_KEY = 'fpwzZRsVN2jkAkUD9hvYQ5'
    #AWS_STORAGE_BUCKET_NAME = 'winwindeal'
   # AWS_S3_ENDPOINT_URL = 'https://hb.ru-1.storage.cloud.mail.ru'
   # AWS_S3_REGION_NAME = 'ru-1'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'goldinpav@yandex.ru'
EMAIL_HOST_PASSWORD = 'mglkpkdkfapyubfa'
DEFAULT_FROM_EMAIL = 'WinWinDeal <goldinpav@yandex.ru>'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
YOOMONEY_ACCOUNT_ID = '1105130'
YOOMONEY_SECRET_KEY = 'test_evMMyWGLIawYaOMUELuBxzSO5XJbnaDcrJeulp2lX8w'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True


class OwnerAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if os.path.exists('package.json'):
    with open('package.json', 'w') as f:
        f.write('{"private": true, "scripts": {}}')

