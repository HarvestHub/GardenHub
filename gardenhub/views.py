from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import (
    FormView, CreateView, UpdateView, DeletionMixin
)
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from sorl.thumbnail import get_thumbnail
from .models import Garden, Plot, Pick, Order
from .forms import (
    OrderForm,
    GardenForm,
    PlotForm,
    ActivateAccountForm,
    AccountSettingsForm
)
from .mixins import UserCanEditGardenMixin, UserCanEditPlotMixin


class LogoutView(LogoutView):
    """
    Logs out the user and redirects them to the login screen.
    """
    next_page = reverse_lazy('login')

    def get_next_page(self):
        # Notify the user that their logout was successful
        messages.add_message(
            self.request, messages.SUCCESS,
            "You've been successfully logged out."
        )
        return super().get_next_page()


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


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    This is a form used to submit a new order. It's used by gardeners, garden
    managers, or anyone who has the ability to edit a plot.
    """
    model = Order
    form_class = OrderForm

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        # Constrain Plot choices
        # We have to do this here because we can access the Request
        form.fields['plot'].queryset = self.request.user.get_plots()

        # Prevent overlapping order dates
        # http://wiki.c2.com/?TestIfDateRangesOverlap
        if form.is_valid():
            data = form.cleaned_data

            overlapping_orders = Order.objects.filter(
                # On the same plot, and
                Q(plot__id=data['plot'].id) &
                (
                    # Start date occurs before the end date, and
                    Q(start_date__lte=data['end_date']) &
                    # End date occurs after the start date
                    Q(end_date__gte=data['start_date'])
                )
            ).active()  # Only active orders matter in this context

            if overlapping_orders.count() > 0:
                # Overlapping orders have been found!
                form.add_error(None, ValidationError(
                    "Dates overlap with another order on this plot. Please "
                    "cancel the other order(s) or select a different date "
                    "range.",
                    code='overlap'
                ))

        return form

    def get_form_kwargs(self):
        # Force Order values: canceled and requester
        order = Order(canceled=False, requester=self.request.user)
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': order})
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)  # Sets self.object
        order = self.object
        # Notify pickers on this order's garden that there's a new order
        pickers = order.plot.garden.pickers.all()
        for picker in pickers:
            picker.email_user(
                subject="New order on plot {} in {}".format(
                    order.plot.title, order.plot.garden.title),
                message=render_to_string(
                    'gardenhub/email_picker_new_order.txt', {
                        'picker': picker,
                        'order': order
                    }
                )
            )
        # Friendly confirmation message
        messages.add_message(
            self.request, messages.SUCCESS,
            "Your order was successfully submitted!"
        )
        return response

    def test_func(self):
        # Ensure the user has the ability to edit at least 1 plot
        return self.request.user.is_gardener()


class PickCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Form enabling a picker to submit a Pick for a given plot.
    """
    model = Pick
    fields = ['crops']
    success_url = reverse_lazy('home')

    def test_func(self):
        # Reject non-Pickers from this view
        return self.request.user.is_picker()

    def get_form_kwargs(self):
        # Set the pick's plot and requester
        plot = get_object_or_404(Plot, id=self.kwargs['plotId'])
        pick = Pick(plot=plot, picker=self.request.user)
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': pick})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plot'] = get_object_or_404(Plot, id=self.kwargs['plotId'])
        return context

    def form_valid(self, form):
        response = super().form_valid(form)  # Sets self.object
        pick = self.object
        # Notify Pick inquirers
        for inquirer in pick.inquirers():
            inquirer.email_user(
                subject="Plot {} in {} has been picked!".format(
                    pick.plot.title, pick.plot.garden.title),
                message=render_to_string(
                    'gardenhub/email_inquirer_new_pick.txt', {
                        'inquirer': inquirer,
                        'pick': pick
                    }
                )
            )
        return response


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


class OrderCancelView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('order-list')
    template_name_suffix = '_confirm_cancel'

    def delete(self, request, *args, **kwargs):
        order = self.object = self.get_object()
        success_url = self.get_success_url()

        order.canceled = True
        order.canceled_timestamp = timezone.now()
        order.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            "You've successfully canceled order #{}.".format(order.id)
        )

        return HttpResponseRedirect(success_url)

    def test_func(self):
        order = self.get_object()
        is_manager = self.request.user.can_edit_order(order)
        return is_manager and order.is_open()


class GardenListView(LoginRequiredMixin, ListView):
    """
    A list of all gardens the logged-in user can edit.
    """
    context_object_name = 'gardens'

    def get_queryset(self):
        return self.request.user.get_gardens()


class GardenDetailView(LoginRequiredMixin, UserCanEditGardenMixin, DetailView):
    """
    View a single garden.
    """
    model = Garden


class GardenUpdateView(LoginRequiredMixin, UserCanEditGardenMixin, UpdateView):
    """
    Edit form for an individual garden.
    """
    model = Garden
    form_class = GardenForm

    def form_valid(self, form):
        response = super().form_valid(form)
        # Get user objects from email addresses and invite everyone else
        managers = get_user_model().objects.get_or_invite_users(
            form.cleaned_data['manager_emails'],  # Submitted emails
            self.request  # The email template needs request data
        )
        self.object.managers.set(managers)
        messages.add_message(
            self.request, messages.SUCCESS,
            "Garden {} has been successfully updated!".format(
                self.object.title)
        )
        self.object.save()  # FIXME: Prevent saving the object twice
        return response


class PlotListView(LoginRequiredMixin, ListView):
    """
    A list of all plots the logged-in user can edit.
    """
    context_object_name = 'plots'

    def get_queryset(self):
        return self.request.user.get_plots()


class PlotCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Plot
    form_class = PlotForm
    success_url = reverse_lazy('plot-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.add_message(
            self.request, messages.SUCCESS,
            "Plot {} has been successfully created!".format(self.object.title)
        )
        return response

    def test_func(self):
        # Only garden managers can create plots
        return self.request.user.is_garden_manager()


class PlotUpdateView(LoginRequiredMixin, UserCanEditPlotMixin, UpdateView):
    """
    Edit form for an individual plot.
    """
    model = Plot
    form_class = PlotForm
    success_url = reverse_lazy('plot-list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        garden = self.object.garden
        garden_field = form.fields['garden']
        # Garden options should be all gardens the user can manage
        # plus the current Plot's garden
        garden_queryset = Garden.objects.filter(
            Q(id=garden.id) |
            Q(managers__id=self.request.user.id)
        )
        # Constrain Garden choices
        # We have to do this here because we can access the Request
        garden_field.queryset = garden_queryset
        # Only managers of the plot's garden can change its garden and name
        if not self.request.user.can_edit_garden(garden):
            garden_field.disabled = True
            form.fields['title'].disabled = True
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        # Get user objects from email addresses and invite everyone else
        gardeners = get_user_model().objects.get_or_invite_users(
            form.cleaned_data['gardener_emails'],  # Submitted emails
            self.request  # The email template needs request data
        )
        self.object.gardeners.set(gardeners)
        self.object.save()  # FIXME: Prevent saving the object twice
        messages.add_message(
            self.request, messages.SUCCESS,
            "Plot {} has been successfully updated!".format(self.object.title)
        )
        return response


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
        return HttpResponseRedirect(reverse_lazy('home'))

    # Form has been submitted
    if request.method == 'POST':
        form = ActivateAccountForm(request.POST)

        # TODO: Bake this into form.is_valid()?
        passwords_match = form.cleaned_data['password1'] \
            == form.cleaned_data['password2']

        if form.is_valid() and passwords_match:
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = True
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # TODO: Actually authenticate the user
            return HttpResponseRedirect(reverse_lazy('home'))

    return render(request, 'gardenhub/account_activate.html')


class AccountView(LoginRequiredMixin, TemplateView):
    """
    Profile edit screen for the logged-in user.
    """
    template_name = 'gardenhub/account_detail.html'


class AccountSettingsView(LoginRequiredMixin, FormView):
    """
    Account settings screen for the logged-in user.
    """
    template_name = 'gardenhub/account_settings.html'
    form_class = AccountSettingsForm
    success_url = reverse_lazy('account-settings')

    def form_valid(self, form):
        user = self.request.user

        # Set user's name
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']

        # Set photo
        user.photo = form.cleaned_data['photo']

        # Set password if it's entered
        pass1 = form.cleaned_data['new_password1']
        pass2 = form.cleaned_data['new_password2']
        oldpass = form.cleaned_data['password']

        has_passwords = oldpass and pass1 and pass2

        # Only applicable if the user entered data into the password fields
        if has_passwords:
            passwords_match = pass1 == pass2
            valid_oldpass = user.check_password(oldpass)

            if valid_oldpass and passwords_match:
                user.set_password(pass1)
                messages.add_message(
                    self.request, messages.SUCCESS,
                    "Account successfully updated."
                )
            elif not valid_oldpass:
                messages.add_message(
                    self.request, messages.ERROR,
                    "You entered the wrong password."
                )
            else:
                messages.add_message(
                    self.request, messages.ERROR,
                    "The given passwords do not match."
                )
        # If the user did *not* enter passwords...
        else:
            messages.add_message(
                self.request, messages.SUCCESS, "Profile successfully updated."
            )

        # Save user object
        user.save()

        return super().form_valid(form)


class AccountRemoveView(LoginRequiredMixin, DeletionMixin, TemplateView):
    """
    Remove the logged-in user's GardenHub account.
    """
    template_name = 'gardenhub/account_confirm_remove.html'
    success_url = reverse_lazy('logout')

    def delete(self, request, *args, **kwargs):
        user = self.object = request.user
        success_url = self.get_success_url()

        user.is_active = False
        user.save()

        messages.add_message(
            self.request, messages.SUCCESS,
            "You've successfully removed your account."
        )

        return HttpResponseRedirect(success_url)


class ApiCrops(LoginRequiredMixin, UserCanEditPlotMixin, DetailView):
    """
    Return JSON about crops.
    """
    model = Plot

    def get(self, request, *args, **kwargs):
        super().get(self, request, *args, **kwargs)
        try:
            crops = self.object.crops.all()
            return JsonResponse({
                "crops": [{
                    "id": crop.id,
                    "title": crop.title,
                    "image": get_thumbnail(
                        crop.image, '125x125', crop='center').url
                } for crop in crops]})

        except Exception:
            return JsonResponse({})
