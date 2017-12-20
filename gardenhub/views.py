import math
import time
import uuid
from datetime import datetime, timedelta
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
)
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.base import TemplateView
from sorl.thumbnail import get_thumbnail
from .models import Crop, Garden, Plot, Harvest, Order, Affiliation
from .forms import (
    CreateOrderForm,
    EditGardenForm,
    EditPlotForm,
    ActivateAccountForm,
    AccountSettingsForm
)
from .decorators import (
    can_edit_plot,
    can_edit_garden,
    can_edit_order
)


def login_view(request):
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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            context['login_failed'] = True

    # Display a success message if the user just logged out
    try:
        del request.session['loggedout']
        context['loggedout'] = True
    except KeyError:
        pass

    return render(request, 'gardenhub/login.html', context)


def logout_view(request):
    """
    Logs out the user and redirects them to the login screen.
    """
    logout(request)
    # Pass a token to the login screen so it can display a success message
    request.session['loggedout'] = True
    return HttpResponseRedirect('/')


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Welcome screen with calls to action.
    """
    template_name = 'gardenhub/homepage.html'


class OrderListView(LoginRequiredMixin, ListView):
    """
    Manage orders page to view all upcoming orders.
    """
    context_object_name = 'orders'

    def get_queryset(self):
        return self.request.user.get_orders()


@login_required
def order_create_view(request):
    """
    This is a form used to submit a new order. It's used by gardeners, garden
    managers, or anyone who has the ability to edit a plot.
    """
    context = {}

    # A form has been submitted
    if request.method == 'POST':
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
    return render(request, 'gardenhub/order_create.html', context)


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Review an individual order that's been submitted. Anyone who can edit the
    plot may view or cancel these orders.
    """
    model = Order

    def test_func(self):
        # Can the user manage this order?
        is_manager = self.request.user.can_edit_order(self.get_object())
        # Should the user pick this order?
        is_picker = self.request.user.is_order_picker(self.get_object())
        # Is the user a manager or picker of this order?
        return is_manager or is_picker


class GardenListView(LoginRequiredMixin, ListView):
    """
    A list of all gardens the logged-in user can edit.
    """
    context_object_name = 'gardens'

    def get_queryset(self):
        return self.request.user.get_gardens()


class GardenDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    View a single garden.
    """
    model = Garden

    def test_func(self):
        # Test that the user can edit this garden
        return self.request.user.can_edit_garden(self.get_object())


@login_required
@can_edit_garden
def garden_update_view(request, pk):
    """
    Edit form for an individual garden.
    """
    context = {}
    garden = get_object_or_404(Garden, id=pk)

    # A form has been submitted
    if request.method == 'POST':
        # Pass data into the form
        form = EditGardenForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Get user objects from email addresses and invite everyone else
            managers = get_user_model().objects.get_or_invite_users(
                form.cleaned_data['manager_emails'], # Submitted emails
                request # The email template needs request data
            )
            # FIXME: There has got to be a better way of updating objects than this
            garden.title = form.cleaned_data['title']
            garden.address = form.cleaned_data['address']
            garden.managers.set(managers)
            garden.save()
            context["success"] = True
    else:
        form = EditGardenForm()

    context["garden"] = garden
    context["form"] = form

    return render(request, 'gardenhub/garden_update.html', context)


class PlotListView(LoginRequiredMixin, ListView):
    """
    A list of all plots the logged-in user can edit.
    """
    context_object_name = 'plots'

    def get_queryset(self):
        return self.request.user.get_plots()


@login_required
@can_edit_plot
def plot_update_view(request, pk):
    """
    Edit form for an individual plot.
    """
    plot = get_object_or_404(Plot, id=pk)

    context = {}

    # A form has been submitted
    if request.method == 'POST':
        # Pass data into the form
        form = EditPlotForm(request.user, request.POST)
        # Check if the form is valid
        if form.is_valid():
            # Get user objects from email addresses and invite everyone else
            gardeners = get_user_model().objects.get_or_invite_users(
                form.cleaned_data['gardener_emails'], # Submitted emails
                request # The email template needs request data
            )
            # FIXME: There has got to be a better way of updating objects than this
            plot.title = form.cleaned_data['title']
            plot.garden = form.cleaned_data['garden']
            plot.gardeners.set(gardeners)
            plot.crops.set(form.cleaned_data['crops'])
            plot.save()
            context["success"] = True
    else:
        form = EditPlotForm(request.user)

    context["form"] = form
    context["plot"] = plot
    context["crops"] = Crop.objects.all()

    return render(request, 'gardenhub/plot_update.html', context)


def account_activate_view(request, token):
    """
    When a new user is invited, an email call to action will send them to this
    view so they can fill out their profile and activate their account.
    """
    user = get_object_or_404(get_user_model(), activation_token=token)

    # The user is already active, this token isn't needed.
    if user.is_active:
        user.activation_token = None
        user.save()
        return HttpResponseRedirect('/')

    context = {}

    # Form has been submitted
    if request.method == 'POST':
        form = ActivateAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['password1'] == form.cleaned_data['password2']:
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = True
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # TODO: Actually authenticate the user
            return HttpResponseRedirect('/')

    return render(request, 'gardenhub/account_activate.html')


class AccountView(LoginRequiredMixin, TemplateView):
    """
    Profile edit screen for the logged-in user.
    """
    template_name = 'gardenhub/account.html'


@login_required
def account_settings_view(request):
    """
    Account settings screen for the logged-in user.
    """

    context = {}

    # Form has been submitted
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            # Set password if it's entered
            if form.cleaned_data['password']:
                if form.cleaned_data['new_password1'] == form.cleaned_data['new_password2']:
                    request.user.set_password(form.cleaned_data['new_password1'])

            context['success'] = True
            request.user.save()

    return render(request, 'gardenhub/account_settings.html', context)


# TODO: Make this actually deactivate the user's account
class DeleteAccountView(LoginRequiredMixin, TemplateView):
    """
    Delete the logged-in user's GardenHub account.
    """
    template_name = 'gardenhub/account_delete.html'


@login_required
@can_edit_plot
def api_crops(request, pk):
    """
    Return JSON about crops.
    """
    try:
        plot = get_object_or_404(Plot, id=pk)
        crops = plot.crops.all()
        return JsonResponse({
            "crops": [{
                "id": crop.id,
                "title": crop.title,
                "image": get_thumbnail(crop.image, '125x125', crop='center').url
            } for crop in crops] })

    except:
        return JsonResponse({})
