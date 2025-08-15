import logging

import reversion
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from fbomatic.forms import TopUpForm
from fbomatic.models import Refueling

logger = logging.getLogger(__name__)


@login_required(login_url=reverse_lazy("fbomatic:index"))
def top_up(request):
    form = TopUpForm(request.POST)

    if not form.is_valid():
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    pump, quantity, price = form.cleaned_data["pump"], form.cleaned_data["quantity"], form.cleaned_data["price"]

    try:
        with reversion.create_revision():
            pump.remaining += quantity
            pump.save()

            Refueling.objects.create(
                pump=pump,
                user=request.user,
                aircraft=None,
                counter=pump.counter,
                quantity=-quantity,
                price=price,
            )

            reversion.set_user(request.user)
            reversion.set_comment("Pump top-up operation")
    except IntegrityError:
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    send_mail(
        f"{settings.EMAIL_SUBJECT_PREFIX}"
        f"Pump topped-up by {request.user.first_name} {request.user.last_name} ({quantity} L)",
        settings.EMAIL_CONTENTS,
        settings.NOTIFICATIONS_EMAIL_FROM,
        [settings.NOTIFICATIONS_EMAIL_TO],
    )

    messages.success(request, _("Pump top-up recorded"))
    return HttpResponseRedirect(reverse("fbomatic:index"))
