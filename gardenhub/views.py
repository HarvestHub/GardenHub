import math
import time
from datetime import datetime, timedelta

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Crop, Garden, Plot, Harvest, Order
from .helpers import is_gardener, is_garden_manager, has_open_orders


def login_user(request):
    context = {}

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            context['login_failed'] = True

    return render(request, 'gardenhub/auth/login.html', context)


@login_required()
def home(request):
    if has_open_orders(request.user):
        # Nothing gets returned after this. I left it for progeny.
        return render(request, 'gardenhub/home/index.html', {
            "user_is_gardener": is_gardener(request.user),
            "user_is_garden_manager": is_garden_manager(request.user),
            "orders": Order.objects.filter(plot__gardeners__id=request.user.id),
        })
    else:
        return render(request, 'gardenhub/home/welcome.html', {
            "user_is_gardener": is_gardener(request.user),
            "user_is_garden_manager": is_garden_manager(request.user),
        })


def orders(request):
    orders = Order.objects.filter(plot__gardeners__id=request.user.id)
    return render(request, 'gardenhub/order/list.html', {
        "orders": orders
    })


def new_order(request):
    return render(request, 'gardenhub/order/create.html')


def view_order(request, orderId):
    order = Order.objects.get(id=orderId)
    return render(request, 'gardenhub/order/view.html', {
        "order": order
    })


def edit_order(request, orderId):
    order = Order.objects.get(id=orderId)
    return render(request, 'gardenhub/order/edit.html', {
        "order": order
    })


def plots(request):
    # TODO: plots = Plot.objects...
    return render(request, 'gardenhub/plot/list.html', {
        # "plots": plots
    })


def edit_plot(request, plotId):
    # TODO: plot = Plot.objects...
    return render(request, 'gardenhub/plot/edit.html', {
        "plot": plot
    })


def gardens(request):
    # TODO: gardens = Garden.objects...
    return render(request, 'gardenhub/garden/list.html', {
        # "gardens": gardens
    })


def edit_garden(request, gardenId):
    # TODO: garden = Garden.objects...
    return render(request, 'gardenhub/garden/edit.html', {
        # "garden": garden
    })


def my_account(request):
    return render(request, 'gardenhub/account/my_account.html')


def account_settings(request):
    return render(request, 'gardenhub/account/edit_settings.html')


def delete_account(request):
    return render(request, 'gardenhub/account/delete_account.html')
