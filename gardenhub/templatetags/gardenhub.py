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
