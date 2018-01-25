from datetime import datetime
from django.utils import timezone


def today():
    return timezone.localtime().replace(
        hour=0, minute=0, second=0, microsecond=0)


def localdate(date):
    return timezone.make_aware(
        datetime(date.year, date.month, date.day))
