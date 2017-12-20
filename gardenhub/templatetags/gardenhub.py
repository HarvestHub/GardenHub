from django import template
from collections import defaultdict

register = template.Library()


@register.simple_tag(takes_context=True)
def garden_user_orders(context, garden):
    """
    Return the user's Orders for the given Garden.
    """
    user = context.request.user
    orders = user.get_orders().filter(plot__garden__id=garden.id)
    return orders


@register.simple_tag(takes_context=True)
def plot_user_orders(context, plot):
    """
    Return the user's Orders for the given Plot.
    """
    user = context.request.user
    orders = user.get_orders().filter(plot__id=plot.id)
    return orders


@register.simple_tag
def placeholder(size, obj):
    letter = str(obj)[0]
    return "//via.placeholder.com/{}/a333c8/ffffff?text={}".format(size, letter)


@register.filter
def combine(value, queryset):
    """
    Unites two querysets and returns distinct values
    """
    return value.union(queryset).distinct()


@register.filter
def picker_format(value, garden):
    """
    Format Orders for the Picker view.
    """
    return value.filter(plot__garden__id=garden.id).active().order_by('-plot__picks__datetime', 'plot__title')
