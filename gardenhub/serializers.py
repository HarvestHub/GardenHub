from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Crop, Garden, Plot, Harvest


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
        model = get_user_model()
        fields = ('id', 'username')
