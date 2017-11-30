from django import template
from gardenhub.helpers import get_orders

register = template.Library()


@register.simple_tag(takes_context=True)
def garden_user_orders(context, garden):
    """
    Return the user's Orders for the given Garden.
    """
    orders = get_orders(context.request.user).filter(plot__garden__id=garden.id)
    return orders


@register.simple_tag(takes_context=True)
def plot_user_orders(context, plot):
    """
    Return the user's Orders for the given Plot.
    """
    orders = get_orders(context.request.user).filter(plot__id=plot.id)
    return orders
