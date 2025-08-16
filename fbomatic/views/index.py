import logging
from dataclasses import asdict, dataclass

from cuser.forms import AuthenticationForm
from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from fbomatic.forms import ExportForm, FuelingForm, TopUpForm
from fbomatic.models import Pump, Refueling

logger = logging.getLogger(__name__)

REFUELING_RECORDS_LIMIT = 10


def index(request):
    @dataclass(frozen=True, kw_only=True)
    class Context:
        pump: Pump
        auth_form: forms.Form
        fueling_form: forms.Form
        top_up_form: forms.Form
        export_form: forms.Form
        refueling_actions: QuerySet[Refueling]
        actions_caption: str
        refueling_threshold: int
        TIME_ZONE: str

    pump = Pump.objects.first()
    refueling_actions = Refueling.objects.filter(pump=pump)[:REFUELING_RECORDS_LIMIT]

    return render(
        request,
        "fbomatic/index.html",
        context=(
            asdict(
                Context(
                    pump=pump,
                    auth_form=AuthenticationForm(),
                    fueling_form=FuelingForm(initial={"pump": pump}),
                    top_up_form=TopUpForm(initial={"pump": pump}),
                    export_form=ExportForm(initial={"pump": pump}),
                    refueling_actions=refueling_actions,
                    actions_caption=_("Last {count} fueling actions").format(count=REFUELING_RECORDS_LIMIT),
                    refueling_threshold=settings.REFUELING_THRESHOLD_LITERS,
                    TIME_ZONE=settings.TIME_ZONE,
                )
            )
        ),
    )
