from django import forms
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Aircraft, Pump

OUTDATED_VIEW_ERROR = _("Someone has just refueled. Check new entries and try again!")


class PumpForm(forms.Form):
    pump = forms.ModelChoiceField(queryset=Pump.objects.all(), widget=forms.HiddenInput())
    counter = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pump = Pump.objects.first()
        self.initial = {"pump": pump, "counter": pump.counter} if pump is not None else {}

    def get_custom_error_message(self):
        if OUTDATED_VIEW_ERROR in self.non_field_errors():
            error_message = OUTDATED_VIEW_ERROR
        else:
            error_message = _("Invalid form data")
        return error_message

    def clean(self):
        cleaned_data = super().clean()
        pump, counter = cleaned_data.get("pump"), cleaned_data.get("counter")
        if pump is None or pump.counter != counter:
            raise forms.ValidationError(OUTDATED_VIEW_ERROR)
        return cleaned_data


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
