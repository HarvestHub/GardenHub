import math
import time
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Crop, Garden, Plot, Harvest


def login(request):
    return render(request, 'gardenhub/index.html', {
        'foo': 'bar',
    })

def ep_garden_assignments(request):
    return render(request, 'gardenhub/employee_views/ep_garden_assignments.html', {
        'foo': 'bar',
    })

def ep_garden_map(request):
    return render(request, 'gardenhub/employee_views/ep_garden_map.html', {
        'foo': 'bar',
    })

def home(request):
    user_group = 'gardener'

    if user_group == 'employee':
        return render(request, 'gardenhub/employee_views/home.html')
    elif user_group == 'gardener':
        return render(request, 'gardenhub/gardener_views/home.html')
    elif user_group == 'manager':
        return render(request, 'gardenhub/manager_views/home.html')


def edit_plot(request):
    return render(request, 'gardenhub/gardener_views/edit_plot.html', {
        'foo': 'bar',
    })

def my_gardens(request):
    return render(request, 'gardenhub/gardener_views/my_gardens.html', {
        'foo': 'bar',
    })

def schedule(request):
    return render(request, 'gardenhub/gardener_views/schedule.html', {
        'foo': 'bar',
    })

def manage_garden(request):
    return render(request, 'gardenhub/manager_views/manage_garden.html', {
        'foo': 'bar',
    })

def manage_gardens_select(request):
    return render(request, 'gardenhub/manager_views/manage_gardens_select.html', {
        'foo': 'bar',
    })

def view_gardeners(request):
    return render(request, 'gardenhub/manager_views/view_gardeners.html', {
        'foo': 'bar',
    })
