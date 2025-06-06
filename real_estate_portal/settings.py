import sys
import os
from pathlib import Path
from dotenv import load_dotenv  # Для загрузки переменных окружения

# Загрузка переменных окружения из файла .env
load_dotenv()

# Базовые директории
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Безопасность
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-ваш-резервный-ключ-для-разработки')

DEBUG = False
handler500 = 'accounts.views.server_error'
ALLOWED_HOSTS = ['*']


CORS_ALLOW_ALL_ORIGINS = True

# Настройки приложений
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
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

# Настройки шаблонов
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
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

WSGI_APPLICATION = 'real_estate_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', 'railway'),  # 'railway' — значение по умолчанию
        'USER': os.getenv('PGUSER', 'postgres'),
        'PASSWORD': os.getenv('PGPASSWORD', 'qwUAvTjFTpNyQfCEZCSVqbxTecEJRHCP'),
        'HOST': os.getenv('PGHOST', 'trolley.proxy.rlwy.net'),
        'PORT': os.getenv('PGPORT', '15306'),
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
# Интернационализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Для разработки
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Для продакшена (collectstatic)

# Медиа файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Кастомная модель пользователя
AUTH_USER_MODEL = 'accounts.User'

# URL перенаправления
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'




# Настройки почты

# Настройки почты
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'  # Корректный адрес
EMAIL_PORT = 465               # Стандартный порт для SSL
EMAIL_USE_SSL = True           # Обязательно для порта 465
EMAIL_HOST_USER = 'goldinpav@yandex.ru'  # Полный email
EMAIL_HOST_PASSWORD = 'mglkpkdkfapyubfa'  # Создан в аккаунте Яндекса
DEFAULT_FROM_EMAIL = 'WinWinDeal <goldinpav@yandex.ru>'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



class OwnerAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

# Дополнительные настройки для production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if os.path.exists('package.json'):
    with open('package.json', 'w') as f:
        f.write('{"private": true, "scripts": {}}')

