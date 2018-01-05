from datetime import date
from django import forms
from django.forms import ModelForm
from django.core import validators
from django.core.exceptions import ValidationError
from .models import Crop, Order


class MultipleEmailField(forms.MultipleChoiceField):
    def valid_value(self, value):
        try:
            validators.validate_email(value)
            return True
        except ValidationError:
            return False


class CreateOrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['plot', 'crops', 'start_date', 'end_date']

    def clean_start_date(self):
        """ Prevent orders being placed for dates prior to today. """
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
