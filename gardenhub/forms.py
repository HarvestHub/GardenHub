from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import Order, Garden, Plot
from gardenhub.utils import today, localdate


class MultipleEmailField(forms.MultipleChoiceField):
    def valid_value(self, value):
        # Valid values are email addresses
        try:
            validators.validate_email(value)
            return True
        except ValidationError:
            return False


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['plot', 'crops', 'start_date', 'end_date', 'comment']

    def clean_start_date(self):
        """ Prevent orders being placed for dates prior to today. """
        start_date = self.cleaned_data['start_date']
        if localdate(start_date) < today():
            raise ValidationError("You cannot create a backdated order")
        return start_date


class PlotForm(forms.ModelForm):
    gardener_emails = MultipleEmailField()

    class Meta:
        model = Plot
        fields = ['title', 'garden', 'crops']


class GardenForm(forms.ModelForm):
    manager_emails = MultipleEmailField()

    class Meta:
        model = Garden
        fields = ['title', 'address']


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
