from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Plot


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
