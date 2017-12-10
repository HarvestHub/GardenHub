import math
import time
import uuid
from datetime import datetime, timedelta
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
)
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Crop, Garden, Plot, Harvest, Order, Affiliation
from .forms import CreateOrderForm, EditPlotForm, ActivateAccountForm
from .decorators import (
    is_anything,
    can_edit_plot,
    can_edit_garden,
    can_edit_order
)


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


@login_required
@is_anything
def home(request):
    """
    Welcome screen with calls to action.
    """
    return render(request, 'gardenhub/home/welcome.html')


@login_required
@is_anything
def orders(request):
    """
    Manage orders page to view all upcoming orders.
    """
    # Display a "welcome screen" if the user hasn't placed any orders
    if not request.user.has_open_orders():
        return render(request, 'gardenhub/order/list.html')

    # Otherwise, display a list of orders
    else:
        return render(request, 'gardenhub/order/list.html', {
            "orders": request.user.get_orders()
        })


@login_required
@is_anything
def new_order(request):
    """
    This is a form used to submit a new order. It's used by gardeners, garden
    managers, or anyone who has the ability to edit a plot.
    """
    context = {}

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


@login_required
@can_edit_order
def view_order(request, orderId):
    """
    Review an individual order that's been submitted. Anyone who can edit the
    plot may view or cancel these orders.
    """
    order = get_object_or_404(Order, id=orderId)

    return render(request, 'gardenhub/order/view.html', {
        "order": order
    })


@login_required
def gardens(request):
    """
    A list of all gardens the logged-in user can edit.
    """
    gardens = request.user.get_gardens()

    return render(request, 'gardenhub/garden/list.html', {
        "gardens": gardens
    })


@login_required
@can_edit_garden
def view_garden(request, gardenId):
    """
    View a single garden.
    """
    garden = get_object_or_404(Garden, id=gardenId)

    return render(request, 'gardenhub/garden/view.html', {
        "garden": garden
    })


@login_required
@can_edit_garden
def edit_garden(request, gardenId):
    """
    Edit form for an individual garden.
    """
    garden = get_object_or_404(Garden, id=gardenId)
    plots = Plot.objects.filter(garden__id=garden.id)

    return render(request, 'gardenhub/garden/edit.html', {
        "garden": garden,
        "plots": plots
    })


@login_required
def plots(request):
    """
    A list of all plots the logged-in user can edit.
    """
    plots = request.user.get_plots()

    return render(request, 'gardenhub/plot/list.html', {
        "plots": plots
    })


@login_required
@can_edit_plot
def edit_plot(request, plotId):
    """
    Edit form for an individual plot.
    """
    plot = get_object_or_404(Plot, id=plotId)

    context = {}

    # A form has been submitted
    if request.POST:
        form = EditPlotForm(request.user, request.POST)
        if form.is_valid():
            gardeners = form.cleaned_data['gardeners']

            gardener_users = []
            for gardener in gardeners:
                user, created = get_user_model().objects.get_or_create(email=gardener)
                if created:
                    user.activation_token = str(uuid.uuid4())
                    user.save()
                    activate_url = request.build_absolute_uri('/activate/{}/'.format(user.activation_token))
                    user.email_user(
                        subject="You've been invited to manage a plot on GardenHub!",
                        message="Hi there! You've been invited to GardenHub. Click here to activate your account: {}".format(activate_url)
                    )
                gardener_users.append(user)

            # FIXME: There has got to be a better way of doing complex forms
            plot.title = form.cleaned_data['title']
            plot.garden = form.cleaned_data['garden']
            plot.gardeners.set(gardener_users)
            plot.crops.set(form.cleaned_data['crops'])
            plot.save()
            context["success"] = True
    else:
        form = EditPlotForm(request.user)

    context["form"] = form
    context["plot"] = plot
    # FIXME: This should only pull in gardeners from the selected garden
    context["gardeners"] = get_user_model().objects.all()
    context["crops"] = Crop.objects.all()

    return render(request, 'gardenhub/plot/edit.html', context)


def activate_account(request, uuid):
    """
    When a new user is invited, an email call to action will send them to this
    view so they can fill out their profile and activate their account.
    """
    user = get_object_or_404(get_user_model(), activation_token=uuid)

    # The user is already active, this token isn't needed.
    if user.is_active:
        user.activation_token = None
        user.save()
        return HttpResponseRedirect('/')

    context = {}

    # Form has been submitted
    if request.POST:
        form = ActivateAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['password1'] == form.cleaned_data['password2']:
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = True
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # TODO: Actually authenticate the user
            return HttpResponseRedirect('/')

    return render(request, 'gardenhub/auth/activate.html')


@login_required
def my_account(request):
    """
    Profile edit screen for the logged-in user.
    """
    gardens = request.user.get_gardens()

    return render(request, 'gardenhub/account/my_account.html', {
        "gardens": gardens
})


@login_required
def account_settings(request):
    """
    Account settings screen for the logged-in user.
    """
    return render(request, 'gardenhub/account/edit_settings.html')


@login_required
def delete_account(request):
    """
    Delete the logged-in user's GardenHub account.
    """
    return render(request, 'gardenhub/account/delete_account.html')


@login_required
@can_edit_plot
def api_crops(request, plotId):
    """
    Return JSON about crops.
    """
    try:
        plot = get_object_or_404(Plot, id=plotId)
        crops = plot.crops.all()
        return JsonResponse({
            "crops": [{
                "id": crop.id,
                "title": crop.title,
                "image": crop.image.url
            } for crop in crops] })

    except:
        return JsonResponse({})
