from datetime import timedelta
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from gardenhub.models import Order, Garden, Plot, Crop
from gardenhub.utils import today, localdate


class MultipleEmailField(forms.MultipleChoiceField):
    def clean(self, value):
        values = super().clean(value)
        emails = [email.lower() for email in values]
        return list(set(emails))

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
        start_date = self.cleaned_data['start_date']

        # Prevent orders with a start_date before today
        if localdate(start_date) < today():
            raise ValidationError("You cannot create a backdated order")

        # Prevent orders with less than a day's notice
        if localdate(start_date) < today() + timedelta(days=1):
            raise ValidationError("Please allow 24 hours between now "
                                  "and the start of your order")
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
    gardener_emails = MultipleEmailField(required=False)

    class Meta:
        model = Plot
        fields = ['title', 'garden', 'crops']


class GardenForm(forms.ModelForm):
    manager_emails = MultipleEmailField(required=False)

    class Meta:
        model = Garden
        fields = ['title', 'address', 'map_image']


class ActivateAccountForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = PhoneNumberField(required=False)
    password1 = forms.CharField()
    password2 = forms.CharField()


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = PhoneNumberField(required=False)
    photo = forms.ImageField(required=False)
    password = forms.CharField(required=False)
    new_password1 = forms.CharField(required=False)
    new_password2 = forms.CharField(required=False)
