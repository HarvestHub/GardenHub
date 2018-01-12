from datetime import datetime
from django.utils import timezone


today = lambda: timezone.localtime().replace(
    hour=0, minute=0, second=0, microsecond=0
)

localdate = lambda date: timezone.make_aware(
    datetime(date.year, date.month, date.day)
)
