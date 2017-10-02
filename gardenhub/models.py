from django.db import models
from django.contrib.auth.models import User


class Crop(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField()

    def __str__(self):
        return self.title


class Garden(models.Model):
    title = models.CharField(max_length=255)
    managers = models.ManyToManyField(User, related_name='+')
    address = models.CharField(max_length=255)
    gardeners = models.ManyToManyField(User, related_name='+')

    def __str__(self):
        return self.title


class Plot(models.Model):
    title = models.CharField(max_length=255)
    garden = models.ForeignKey('Garden')
    gardener = models.ManyToManyField(User)
    crops = models.ManyToManyField('Crop')

    def __str__(self):
        return self.title


class Order(models.Models):

    plot = models.ForeignKey('Plot')
    crops = models.ManyToManyField('Crop')
    start_date = models.DateField()
    end_date = models.DateField()
    canceled = models.BooleanField
    canceled_date = models.DateField(null=True, blank=True)
    requester = models.ForeignKey(User)

        def __str__(self):
            return self.id


class Harvest(models.Model):

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
        return self.id
