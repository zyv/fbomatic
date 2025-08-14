import logging

import reversion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fbomatic.forms import FuelingForm
from fbomatic.models import Pump, Refueling

logger = logging.getLogger(__name__)


@login_required
def refuel(request):
    form = FuelingForm(request.POST)

    if not form.is_valid():
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    quantity = form.cleaned_data["quantity"]

    with transaction.atomic():
        pump = Pump.objects.first()

        if pump.remaining < quantity:
            messages.error(request, _("Not enough fuel in the pump"))
            return HttpResponseRedirect(reverse("fbomatic:index"))

        with reversion.create_revision():
            pump.remaining = F("remaining") - quantity
            pump.counter = F("counter") + quantity
            pump.save()

            pump.refresh_from_db()

            Refueling.objects.create(
                pump=pump,
                user=request.user,
                aircraft=form.cleaned_data["aircraft"],
                counter=pump.counter,
                quantity=quantity,
            )

            reversion.set_user(request.user)
            reversion.set_comment("Refueling operation")

            # TODO mail

    messages.success(request, _("Refueling recorded"))
    return HttpResponseRedirect(reverse("fbomatic:index"))
