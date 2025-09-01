from django import forms
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Aircraft, Pump


class PumpForm(forms.Form):
    pump = forms.ModelChoiceField(queryset=Pump.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial = {"pump": Pump.objects.first()}


class FuelingForm(PumpForm):
    aircraft = forms.ModelChoiceField(label=_("Registration"), queryset=Aircraft.objects.all())
    quantity = forms.IntegerField(
        label=_("Quantity"),
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "123"}),
    )


class TopUpForm(PumpForm):
    quantity = forms.IntegerField(
        label=_("Quantity"),
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "321"}),
    )
    price = forms.DecimalField(
        label=_("Price"),
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "1.234"}),
    )


class ExportForm(PumpForm):
    count = forms.IntegerField(label=_("Number of records"), initial=500, min_value=1)
