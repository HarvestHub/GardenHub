from datetime import date
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

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date < date.today():
            raise ValidationError("You cannot create a backdated order")
        return start_date


class EditPlotForm(forms.Form):
    title = forms.CharField()
    garden = forms.ModelChoiceField(queryset=None)
    gardener_emails = MultipleEmailField()
    crops = forms.ModelMultipleChoiceField(queryset=Crop.objects.all())

    def __init__(self, user, *args, **kwargs):
        super(EditPlotForm, self).__init__(*args, **kwargs)
        self.fields['garden'].queryset = user.get_gardens()


class EditGardenForm(forms.Form):
    title = forms.CharField()
    address = forms.CharField()
    manager_emails = MultipleEmailField()


class CreatePickForm(forms.Form):
    crops = forms.ModelMultipleChoiceField(queryset=Crop.objects.all())


class ActivateAccountForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(required=False)
    new_password1 = forms.CharField(required=False)
    new_password2 = forms.CharField(required=False)
