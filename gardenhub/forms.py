from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from .models import Order, Garden, Plot, Crop
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
        fields = ['plot', 'start_date', 'end_date',
                  'pick_all', 'crops', 'comment']

    def clean_start_date(self):
        """ Prevent orders being placed for dates prior to today. """
        start_date = self.cleaned_data['start_date']
        if localdate(start_date) < today():
            raise ValidationError("You cannot create a backdated order")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        pick_all = cleaned_data["pick_all"]
        crops = cleaned_data["crops"]

        if not pick_all and not crops:
            raise forms.ValidationError(
                "Please indicate which crops you'd like picked.")

        if pick_all is True:
            cleaned_data["crops"] = Crop.objects.none()

        return cleaned_data


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
    photo = forms.ImageField(required=False)
    password = forms.CharField(required=False)
    new_password1 = forms.CharField(required=False)
    new_password2 = forms.CharField(required=False)
