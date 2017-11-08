from .models import Garden, Plot


def is_gardener(user):
    """
    A gardener is someone who rents a garden Plot and grows food there.
    Gardeners are assigned to Plot.gardener on at least one Plot.
    """
    return Plot.objects.filter(gardeners__id=user.id).count() > 0


def is_garden_manager(user):
    """
    A garden manager is someone who facilitates renting Plots of a Garden out to
    Gardeners. Any person who is set as Garden.manager on at least one Garden.
    """
    return Garden.objects.filter(managers__id=user.id).count() > 0
