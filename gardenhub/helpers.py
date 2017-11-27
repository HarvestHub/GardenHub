from django.db.models import Q
from .models import Garden, Plot, Order


def get_gardens(user):
    """
    Return all the Gardens the given user can edit.
    """
    return Garden.objects.filter(managers__id=user.id)


def get_plots(user):
    """
    Return all the Plots the given user can edit. Users can edit any plot which
    they are a gardener on, and any plot in a garden they manage.
    """
    return Plot.objects.filter(
        Q(gardeners__id=user.id) | Q(garden__managers__id=user.id)
    ).distinct()


def get_orders(user):
    """
    Return all Orders for the given user's Plots and Gardens.
    """
    plot_ids = [ plot.id for plot in get_plots(user).all() ]
    return Order.objects.filter(plot__id__in=plot_ids)


def is_garden_manager(user):
    """
    A garden manager is someone who facilitates renting Plots of a Garden out to
    Gardeners. Any person who is set as Garden.manager on at least one Garden.
    """
    return get_gardens(user).count() > 0


def is_gardener(user):
    """
    A gardener is someone who rents a garden Plot and grows food there.
    Gardeners are assigned to Plot.gardener on at least one Plot.
    """
    return get_plots(user).count() > 0


def is_anything(user):
    """
    GardenHub is only useful if the logged-in user can manage any garden or
    plot. If not, that is very sad. :(
    """
    return is_gardener(user) or is_garden_manager(user)


def has_open_orders(user):
    """
    Determine whether or not a user has any current open harvests for home display.
    """
    return get_orders(user).count() > 0


def can_edit_garden(user, garden):
    """
    Can the given user manage this garden?
    True if the user is listed in Garden.managers for that garden.
    False otherwise.
    """
    return user in garden.managers.all()


def can_edit_plot(user, plot):
    """
    Can the given user manage this plot?
    True if the user is listed in Plot.gardeners for that plot, OR the user is
    listed in Garden.managers for the garden in Plot.garden.
    False otherwise.
    """
    return user in plot.gardeners.all() or user in plot.garden.managers.all()
