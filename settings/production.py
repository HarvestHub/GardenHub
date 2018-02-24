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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = env['EMAIL_HOST']
EMAIL_PORT = int(env.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = env['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = env['DEFAULT_FROM_EMAIL']

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

# S3 file storage for media uploads
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = env['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = env['AWS_STORAGE_BUCKET_NAME']
AWS_S3_ENDPOINT_URL = env['AWS_S3_ENDPOINT_URL']
AWS_S3_SIGNATURE_VERSION = 's3v4'

try:
    from .local import *  # noqa
except ImportError:
    pass
