from django import template

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
