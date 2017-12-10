from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import Order, Plot, Garden, Crop


class MultipleEmailField(forms.MultipleChoiceField):
    def valid_value(self, value):
        try:
            validators.validate_email(value)
            return True
        except exceptions.ValidationError as e:
            return False


class CreateOrderForm(forms.Form):
    plot = forms.ModelChoiceField(queryset=None)
    crops = forms.ModelMultipleChoiceField(queryset=Crop.objects.all())
    start_date = forms.DateField()
    end_date = forms.DateField()

    def __init__(self, user, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        self.fields['plot'].queryset = user.get_plots()


class EditPlotForm(forms.Form):
    title = forms.CharField()
    garden = forms.ModelChoiceField(queryset=None)
    gardeners = MultipleEmailField()
    crops = forms.ModelMultipleChoiceField(queryset=Crop.objects.all())

    def __init__(self, user, *args, **kwargs):
        super(EditPlotForm, self).__init__(*args, **kwargs)
        self.fields['garden'].queryset = user.get_gardens()


class ActivateAccountForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()
