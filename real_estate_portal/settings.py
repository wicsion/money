import os
from pathlib import Path
from dotenv import load_dotenv  # Для загрузки переменных окружения

# Загрузка переменных окружения из файла .env
load_dotenv()

# Базовые директории
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-ваш-резервный-ключ-для-разработки')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    '192.168.50.98',  # Ваш локальный IP
    'localhost',       # Для доступа через localhost
    '127.0.0.1',       # Стандартный локальный адрес
]

# Настройки приложений
INSTALLED_APPS = [
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


    # Локальные приложения
    'accounts.apps.AccountsConfig',
    'brokers.apps.BrokersConfig',
    'developers.apps.DevelopersConfig',
    'clients.apps.ClientsConfig',
    'properties.apps.PropertiesConfig',
    'payments.apps.PaymentsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

WSGI_APPLICATION = 'real_estate_portal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
       'NAME': BASE_DIR / 'db.sqlite3',     }
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
MEDIA_ROOT = BASE_DIR / 'media'

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
DEFAULT_FROM_EMAIL = 'RealEstatePro <goldinpav@yandex.ru>'


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