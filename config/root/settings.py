from datetime import timedelta
from pathlib import Path


from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECRET_KEY = config("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    'http://localhost:3000',
    'https://api.fitrat.sector-soft.ru',
    'https://api.ilm.fitrat.sector-soft.ru',
    'https://ilm.fitrat.sector-soft.ru',
    "https://api.ft.sector-soft.ru",
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # "debug_toolbar",

    # Installed apps
    'data.logs',
    'data.account',
    'data.paycomuz',
    'data.clickuz',
    'data.tasks',
    'data.finances.finance',
    'data.finances.compensation',
    'data.finances.timetracker',
    'data.notifications',
    'data.exam_results',

    'data.lid.archived',
    'data.lid.new_lid',

    'data.student.student',
    'data.student.groups',
    'data.student.studentgroup',
    'data.student.lesson',
    'data.student.subject',
    'data.student.attendance',
    'data.student.course',
    'data.student.quiz',
    'data.student.mastering',
    'data.student.homeworks',
    'data.student.appsettings',
    'data.student.shop',

    'data.parents',
    'data.command',

    'data.results',

    'data.comments',
    # 'data.moderator',
    'data.upload',

    'data.dashboard',
    'data.library',
    'data.event',

    'data.department.filial',
    'data.department.marketing_channel',

    # Installed
    "corsheaders",
    "rangefilter",
    # "django_plotly_dash",
    "drf_yasg",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "rest_framework_simplejwt",
    'rest_framework_simplejwt.token_blacklist',

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'root.urls'

REST_FRAMEWORK = {
    "DEFAULT_CACHE_ALIAS": "default",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,  # Adjust the page size as needed
    # 'DEFAULT_RENDERER_CLASSES': [
    #     # 'rest_framework.renderers.BrowsableAPIRenderer',
    #     'rest_framework.renderers.JSONRenderer',
    # ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_BLACKLIST_ENABLED": True,
}

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
            ],
        },
    },
]

WSGI_APPLICATION = 'root.wsgi.application'

PAYCOM_SETTINGS = {
    "KASSA_ID": config("PAYME_ID"),
    "SECRET_KEY": config("PAYME_KEY"),
    "ACCOUNTS": {
        "KEY": "order_id"
    },
}

CLICK_SERVICE_ID = config("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = config("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = config("CLICK_SECRET_KEY")
CLICK_ACCOUNT_MODEL = "clickuz.models.Order"
CLICK_AMOUNT_FIELD = "amount"

CLICK_SETTINGS = {
    "service_id": config("CLICK_SERVICE_ID"),
    "merchant_id": config("CLICK_MERCHANT_ID"),
    "secret_key": config("CLICK_SECRET_KEY"),

    "commission_percent": 0,
    "disable_admin": False,
}

CLICK_COMMISSION_PERCENT = "(optional int field) your companies comission percent if applicable"
CLICK_DISABLE_ADMIN = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default=5434, cast=int),
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            "client_encoding": "UTF8",
        }
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

# USE_TZ = True


STATIC_URL = 'static/'
MEDIA_URL = 'media/'

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'account.CustomUser'
PAYME_ACCOUNT_MODEL = 'data.student.student.models.Student'

DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://fitrat-erp.vercel.app",
    "https://api.fitrat.sector-soft.ru",
    "https://fitrat.sector-soft.ru",
    "https://www.fitrat.sector-soft.ru",
    "https://ilm.fitrat.sector-soft.ru",
    "https://api.ilm.fitrat.sector-soft.ru",
    "https://api.ft.sector-soft.ru",
    "https://ft.sector-soft.ru",
    "https://8fc541a61a9e.ngrok-free.app"
]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "OPTIONS",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "ngrok-skip-browser-warning"
)

CORS_ALLOW_CREDENTIALS = True

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
