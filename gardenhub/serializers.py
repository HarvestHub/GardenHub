from .models import Crop, Garden, Plot, Harvest
from django.contrib.auth.models import User
from rest_framework import serializers


class CropSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Crop
        fields = ('id', 'title')


class GardenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Garden
        fields = ('id', 'title', 'owners')


class PlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Plot
        fields = ('id', 'title', 'garden')


class HarvestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Harvest
        fields = ('id', 'plot', 'crops')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
