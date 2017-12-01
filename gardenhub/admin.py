from django.contrib import admin
from .models import Crop, Garden, Plot, Harvest, Order, Affiliation

admin.site.register(Crop)
admin.site.register(Garden)
admin.site.register(Plot)
admin.site.register(Harvest)
admin.site.register(Order)
admin.site.register(Affiliation)
