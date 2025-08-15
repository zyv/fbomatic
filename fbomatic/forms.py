from django import forms
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Aircraft, Pump


class FuelingForm(forms.Form):
    aircraft = forms.ModelChoiceField(label=_("Registration"), queryset=Aircraft.objects.all())
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1)
    pump = forms.ModelChoiceField(queryset=Pump.objects.all(), widget=forms.HiddenInput())


class TopUpForm(forms.Form):
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1)
    price = forms.DecimalField(label=_("Price"), min_value=1)
    pump = forms.ModelChoiceField(queryset=Pump.objects.all(), widget=forms.HiddenInput())


class ExportForm(forms.Form):
    count = forms.IntegerField(label=_("Number of records"), initial=500, min_value=1)
    pump = forms.ModelChoiceField(queryset=Pump.objects.all(), widget=forms.HiddenInput())
