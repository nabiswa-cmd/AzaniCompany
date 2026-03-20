from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'azani-ispo-secret-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'azani.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'core' / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'azani.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'azani_ispo.db',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Azani Business Constants ──
REGISTRATION_FEE  = Decimal('8500.00')
INSTALLATION_FEE  = Decimal('10000.00')
PC_UNIT_COST      = Decimal('40000.00')
UPGRADE_DISCOUNT  = Decimal('0.10')
OVERDUE_FINE_RATE = Decimal('0.15')
RECONNECTION_FEE  = Decimal('1000.00')

BANDWIDTH_COSTS = {
    4:  Decimal('1200.00'),
    10: Decimal('2000.00'),
    20: Decimal('3500.00'),
    25: Decimal('4000.00'),
    50: Decimal('7000.00'),
}
