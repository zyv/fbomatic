import logging

import reversion
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from fbomatic.forms import FuelingForm
from fbomatic.models import Refueling

logger = logging.getLogger(__name__)


@never_cache
@csrf_protect
@login_required
def refuel(request):
    form = FuelingForm(request.POST)

    if not form.is_valid():
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    pump, quantity = form.cleaned_data["pump"], form.cleaned_data["quantity"]

    try:
        with reversion.create_revision():
            pump.refresh_from_db()
            pump_remaining_before = pump.remaining
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
    except IntegrityError:
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    if (
        pump.remaining < settings.REFUELING_THRESHOLD_LITERS
        and pump_remaining_before >= settings.REFUELING_THRESHOLD_LITERS
    ):
        send_mail(
            f"{settings.EMAIL_SUBJECT_PREFIX}"
            f"Please refill, remaining fuel {pump.remaining} L < {settings.REFUELING_THRESHOLD_LITERS} L",
            settings.EMAIL_CONTENTS,
            settings.NOTIFICATIONS_EMAIL_FROM,
            [settings.NOTIFICATIONS_EMAIL_TO, request.user.email],
        )

    messages.success(request, _("Refueling recorded"))
    return HttpResponseRedirect(reverse("fbomatic:index"))
