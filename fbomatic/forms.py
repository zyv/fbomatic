from django import forms
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Aircraft


class FuelingForm(forms.Form):
    aircraft = forms.ModelChoiceField(label=_("Registration"), queryset=Aircraft.objects.all())
    quantity = forms.IntegerField(label=_("Quantity"), min_value=1)

    # todo remove
    # def is_valid(self):
    #     return False
