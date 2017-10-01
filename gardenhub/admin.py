from django.contrib import admin
from .models import Crop, Garden, Plot, Harvest

admin.site.register(Crop)
admin.site.register(Garden)
admin.site.register(Plot)
admin.site.register(Harvest)
