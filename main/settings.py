import os

"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1vu$+-g+ji#6fm1whskw^x$=f9y^@*tb-)jl#=t$=^e+4!@x+('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
LOGIN_REDIRECT_URL = '/inicio/'
LOGOUT_REDIRECT_URL = '/'

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alicuota.apps.AlicuotaConfig',
    'tailwind',
    'theme',
    'django_browser_reload',
    'rest_framework'
]
SITE_ID = 1

JAZZMIN_SETTINGS = {
    "site_brand": "Configuración",
    "welcome_sign": "Bienvenido a Aca-Software",
    "copyright": "Aca-Software Ltd",
    "user_avatar": None,
    "site_logo": None,
    "custom_css": "css/custom_jazzmin.css",  # Agregar el CSS personalizado aquí

    # Configuración del menú de navegación personalizado
    "topmenu_links": [
        {"name": "Inicio", "url": "inicio", "permissions": ["auth.view_user"]},
    ],
}

TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1",
]
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'main.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'mssql',
        # 'NAME': 'URBANIZACIONES',  # Nombre de la base de datos
        # 'USER': 'acontrerass2_SQLLogin_1',  # Usuario correcto desde la imagen
        # 'PASSWORD': 'bxqydlgkda',  # Verifica la contraseña
        # 'HOST': 'URBANIZACIONES.mssql.somee.com',
        # 'PORT': '1433',  # Puerto por defecto

        "ENGINE": "mssql",
        "NAME": "URBANIZACIONES",
        "HOST": "DESKTOP-EH8RUVP",  # Andy
        # "HOST": "LAPTOPBRIGNER10", # Brigner
        "PORT": "",

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;'
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "alicuota/static",
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuraciones para conexión con un correo
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'acaa83406@gmail.com'
EMAIL_HOST_PASSWORD = 'akqe lqcp vkts ehek'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'