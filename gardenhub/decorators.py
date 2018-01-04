from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Plot, Garden, Order


def is_anything(func):
    """
    Only a user who has access to at least one Plot or Garden may access this.
    """
    def func_wrapper(request, *args, **kwargs):
        # If the user has no assigned gardens or plots...
        if not request.user.is_anything():
            return HttpResponseForbidden(
                "You haven't been assigned to any gardens or plots. "
                "This should never happen. Please contact support. "
                "We're sorry!"
            )
        # Otherwise, carry on
        else:
            return func(request, *args, **kwargs)

    return func_wrapper


def can_edit_plot(func):
    """
    Only a user who can edit this Plot may access this.
    """
    def func_wrapper(request, pk, *args, **kwargs):
        plot = get_object_or_404(Plot, id=pk)

        # If user isn't allowed to edit this plot...
        if not request.user.can_edit_plot(plot):
            return HttpResponseForbidden(
                "You do not have permission to edit this plot.")
        # Otherwise, carry on
        else:
            return func(request, pk, *args, **kwargs)

    return func_wrapper


def can_edit_garden(func):
    """
    Only a user who can edit this Garden may access this.
    """
    def func_wrapper(request, pk, *args, **kwargs):
        garden = get_object_or_404(Garden, id=pk)

        # If the user isn't allowed to edit this garden...
        if not request.user.can_edit_garden(garden):
            return HttpResponseForbidden(
                "You do not have permission to edit this garden.")
        # Otherwise, carry on
        else:
            return func(request, pk, *args, **kwargs)

    return func_wrapper


def can_edit_order(func):
    """
    Only a user who can edit this Order may access this.
    """
    def func_wrapper(request, pk, *args, **kwargs):
        order = get_object_or_404(Order, id=pk)

        # If user isn't allowed to view this order...
        if not request.user.can_edit_order(order):
            return HttpResponseForbidden(
                "You do not have permission to manage this order.")
        # Otherwise, carry on
        else:
            return func(request, pk, *args, **kwargs)

    return func_wrapper
