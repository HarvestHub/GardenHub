from django import forms
from .models import Order, Plot, Crop
from .helpers import get_plots

class CreateOrderForm(forms.Form):
    plot = forms.ModelChoiceField(queryset=None)
    crops = forms.ModelMultipleChoiceField(queryset=Crop.objects.all())
    start_date = forms.DateField()
    end_date = forms.DateField()

    def __init__(self, user, *args, **kwargs):
        super(CreateOrderForm, self).__init__(*args, **kwargs)
        self.fields['plot'].queryset = get_plots(user)
