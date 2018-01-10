import os

from .base import *  # noqa

# Do not set SECRET_KEY, Postgres or LDAP password or any sensitive data here.
# Instead, use environment variables or create a local.py file on the server.

# Disable debug mode
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False  # noqa

env = os.environ.copy()

if 'SECRET_KEY' in env:
    SECRET_KEY = env['SECRET_KEY']

if 'ALLOWED_HOSTS' in env:
    ALLOWED_HOSTS = env['ALLOWED_HOSTS'].split(',')

# Configure email
# https://docs.djangoproject.com/en/2.0/topics/email/
# FIXME: Temporarily use the console backend until real email is implemented
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'me@gmail.com'
# EMAIL_HOST_PASSWORD = 'password'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}

# Makes WhiteNoise work properly.
# http://whitenoise.evans.io/en/stable/django.html#django-compressor
COMPRESS_OFFLINE = True

try:
    from .local import *  # noqa
except ImportError:
    pass
