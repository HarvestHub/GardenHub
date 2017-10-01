from django.db import models
from django.contrib.auth.models import User


class Crop(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Garden(models.Model):
    title = models.CharField(max_length=255)
    owners = models.ManyToManyField(User)

    def __str__(self):
        return self.title


class Plot(models.Model):
    title = models.CharField(max_length=255)
    garden = models.ForeignKey('Garden')

    def __str__(self):
        return self.title


class Harvest(models.Model):
    plot = models.ForeignKey('Plot')
    crops = models.ManyToManyField('Crop')

    def __str__(self):
        return self.id
