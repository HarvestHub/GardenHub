import math
import time
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Crop, Garden, Plot, Harvest


def login(request):
    return render(request, 'gardenhub/login_templates/login.html', {
        'foo': 'bar',
    })

def home(request):
    user_group = 'gardener'

    if user_group == 'employee':
        return render(request, 'gardenhub/homescreen_templates/employee_home.html')
    elif user_group == 'gardener':
        return render(request, 'gardenhub/homescreen_templates/gardener_home.html')
    elif user_group == 'manager':
        return render(request, 'gardenhub/homescreen_templates/manager_home.html')

def account(request):
    return render(request, 'gardenhub/account_settings_templates/my_account.html', {
        'foo': 'bar',
    })

def plot(request):
    return render(request, 'gardenhub/edit_plot_templates/edit_plot.html', {
        'foo': 'bar',
    })

def plot(request):
    return render(request, 'gardenhub/manage_gardens_templates/my_gardens.html', {
        'foo': 'bar',
    })

def harvest(request):
    user_group = 'gardener'

    if user_group == 'employee':
        return render(request, 'gardenhub/harvest_templates/harvest_assignments_templates/_templates/ep_garden_assignments.html')
    elif user_group == 'gardener':
        return render(request, 'gardenhub/harvest_templates/schedule_harvest_templates/schedule.html')
    elif user_group == 'manager':
        return render(request, 'gardenhub/harvest_templates/upcoming_harvest_templates/upcoming_harvests.html')

def manage(request):
    user_group = 'manager'

    if user_group == 'employee':
        return render(request, 'gardenhub/homescreen_templates/employee_home.html')
    elif user_group == 'gardener':
        return render(request, 'gardenhub/homescreen_templates/gardener_home.html')
    elif user_group == 'manager':
        return render(request, 'gardenhub/manage_gardens_templates/my_gardens.html')
