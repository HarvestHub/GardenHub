from django.db import models
from django.contrib.auth.models import User


class Crop(models.Model):
    """
    A crop represents an item that may be harvested, such as a zuchini or an
    orange. Crops are stored in a master list, managed by the site admin, and
    may be listed on Orders or Harvests.
    """
    title = models.CharField(max_length=255)
    image = models.ImageField()

    def __str__(self):
        return self.title


class Garden(models.Model):
    """
    A whole landscape, divided into many plots. Managed by Garden Managers.
    """
    title = models.CharField(max_length=255)
    managers = models.ManyToManyField(User, related_name='+')
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Plot(models.Model):
    """
    Subdivision of a Garden, allocated to a Gardener for growing food.
    """
    title = models.CharField(max_length=255)
    garden = models.ForeignKey('Garden')
    gardener = models.ManyToManyField(User)
    crops = models.ManyToManyField('Crop')

    def __str__(self):
        return self.title


class Order(models.Model):
    """
    A request from a Gardener or Garden Manager to enlist a particular Plot for
    Harvest over a specified number of days.
    """
    plot = models.ForeignKey('Plot')
    crops = models.ManyToManyField('Crop')
    start_date = models.DateField()
    end_date = models.DateField()
    canceled = models.BooleanField
    canceled_date = models.DateField(null=True, blank=True)
    requester = models.ForeignKey(User)

    def __str__(self):
        return str(self.id)


class Harvest(models.Model):
    """
    A submission by an Employee signifying that Crops have been picked from a
    particular Plot on a particular day.
    """
    harvest_date = models.DateField()
    status = models.CharField(
        max_length=255,
        choices=(
            ('incomplete', 'Incomplete'),
            ('finished', 'Finished'),
        ),
    )
    employee = models.ForeignKey(User)

    def __str__(self):
        return str(self.id)


"""
There are several conceptual types of users that we should be aware of.

1. Site Administrator -- Has full access to all data, and is granted the ability
   to invite any new member to the site. TBD: Identifying them programatically.

2. Garden Manager -- Someone who facilitates renting Plots of a Garden out to
   Gardeners. Any person who is set as Garden.manager on at least one Garden.

3. Gardener -- Someone who rents a garden Plot and grows food there. Gardeners
   are assigned to Plot.gardener on at least one Plot.

4. Employee -- A hired employee responsible for fulfilling Orders. It is safe to
   say that anyone with an Order assigned to them is an Employee, but TBD:
   figure out how to determine them programatically when there's no active
   order.
"""
