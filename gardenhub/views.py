import math
import time
from datetime import datetime, timedelta
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
)
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Crop, Garden, Plot, Harvest, Order, Affiliation
from .forms import CreateOrderForm


def login_user(request):
    """
    The main login form that gives people access into the site. It's common
    for people to be redirected here if they don't have permission to view
    something. It's the entrypoint to the whole site.
    """
    context = {}

    # The user is already logged in; redirect them home.
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    # Login credentials have been submitted via the form.
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
    # If the user has no assigned gardens or plots...
    if not request.user.is_anything():
        # TODO: Handle this error better
        return HttpResponse("You haven't been assigned to any gardens or plots. This should never happen. Please contact support. We're sorry!")

    return render(request, 'gardenhub/home/welcome.html')


@login_required()
def orders(request):
    # FIXME: How is this different from the home view?
    # Should we rethink the home view or delete this one?

    """
    Manage orders page to view all upcoming orders. (Previously the home page)
    """
    # If the user has no assigned gardens or plots...
    if not request.user.is_anything():
        # TODO: Handle this error better
        return HttpResponse("You haven't been assigned to any gardens or plots. This should never happen. Please contact support. We're sorry!")

    # Display a "welcome screen" if the user hasn't placed any orders
    if not request.user.has_open_orders():
        return render(request, 'gardenhub/order/list.html')

    # Otherwise, display a list of orders
    else:
        return render(request, 'gardenhub/order/list.html', {
            "orders": request.user.get_orders()
        })


@login_required()
def new_order(request):
    """
    This is a form used to submit a new order. It's used by gardeners, garden
    managers, or anyone who has the ability to edit a plot.
    """
    context = {}

    # If the user has no assigned gardens or plots...
    if not request.user.is_anything():
        # TODO: Handle this error better
        return HttpResponse("You haven't been assigned to any gardens or plots. This should never happen. Please contact support. We're sorry!")

    # A form has been submitted
    if request.POST:
        form = CreateOrderForm(request.user, request.POST)
        if form.is_valid():
            order = Order.objects.create(
                plot=form.cleaned_data['plot'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                canceled=False,
                requester=request.user
            )
            order.crops.set(form.cleaned_data['crops'])
            order.save()
            context["success"] = True
    else:
        form = CreateOrderForm(request.user)

    context["form"] = form
    return render(request, 'gardenhub/order/create.html', context)



@login_required()
def view_order(request, orderId):
    """
    Review an individual order that's been submitted. Anyone who can edit the
    plot may view or cancel these orders.
    """
    order = Order.objects.get(id=orderId)

    # If user isn't allowed to view this order...
    if not request.user.can_edit_plot(order.plot):
        return HttpResponseForbidden()

    return render(request, 'gardenhub/order/view.html', {
        "order": order
    })


@login_required()
def gardens(request):
    """
    A list of all gardens the logged-in user can edit.
    """
    gardens = request.user.get_gardens()
    return render(request, 'gardenhub/garden/list.html', {
        "gardens": gardens
    })


@login_required()
def edit_garden(request, gardenId):
    """
    Edit form for an individual garden.
    """
    garden = Garden.objects.get(id=gardenId)
    plots = Plot.objects.filter(garden__id=garden.id)
    # plots = Plot.objects.get(gardenId=garden_id)

    # If the user isn't allowed to edit this garden...
    if not request.user.can_edit_garden(garden):
        return HttpResponseForbidden()

    return render(request, 'gardenhub/garden/edit.html', {
        "garden": garden,
        "plots": plots
    })


@login_required()
def plots(request):
    """
    A list of all plots the logged-in user can edit.
    """
    plots = request.user.get_plots()
    return render(request, 'gardenhub/plot/list.html', {
        "plots": plots
    })


@login_required()
def edit_plot(request, plotId):
    """
    Edit form for an individual plot.
    """
    plot = Plot.objects.get(id=plotId)
    gardens = request.user.get_gardens()
    # FIXME: This should only pull in gardeners from the selected garden
    gardeners = get_user_model().objects.all()

    # If user isn't allowed to edit this plot...
    if not request.user.can_edit_plot(plot):
        return HttpResponseForbidden()

    return render(request, 'gardenhub/plot/edit.html', {
        "plot": plot,
        "gardens": gardens,
        "gardeners": gardeners
    })


@login_required()
def my_account(request):
    """
    Profile edit screen for the logged-in user.
    """

    gardens = request.user.get_gardens()

    return render(request, 'gardenhub/account/my_account.html', {
        "gardens": gardens
})


@login_required()
def account_settings(request):
    """
    Account settings screen for the logged-in user.
    """
    return render(request, 'gardenhub/account/edit_settings.html')


@login_required()
def delete_account(request):
    """
    Delete the logged-in user's GardenHub account.
    """
    return render(request, 'gardenhub/account/delete_account.html')


@login_required()
def api_crops(request):
    """
    Return JSON about crops.
    """
    try:
        plot = Plot.objects.get(id=request.GET['plot'])

        # If user isn't allowed to edit this plot...
        if not request.user.can_edit_plot(plot):
            return HttpResponseForbidden()

        crops = Plot.objects.get(id=plot.id).crops.all()
        return JsonResponse({
            "crops": [{
                "id": crop.id,
                "title": crop.title,
                "image": crop.image.url
            } for crop in crops] })

    except:
        return JsonResponse({})
