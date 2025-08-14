from django import forms
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Aircraft


class FuelingForm(forms.Form):
    aircraft = forms.ModelChoiceField(label=_("Registration"), queryset=Aircraft.objects.all())
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1)


class TopUpForm(forms.Form):
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1)
    price = forms.DecimalField(label=_("Price"), min_value=1)
