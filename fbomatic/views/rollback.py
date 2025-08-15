import logging

import reversion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from fbomatic.models import Refueling

logger = logging.getLogger(__name__)


@login_required(login_url=reverse_lazy("fbomatic:index"))
@transaction.atomic
def rollback(request):
    latest = Refueling.objects.first()

    if latest is None or (not request.user.is_staff and latest.user != request.user):
        messages.error(request, _("Refueling deletion failed"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    with reversion.create_revision():
        latest.pump.remaining = F("remaining") + latest.quantity
        latest.pump.counter = F("counter") - latest.quantity
        latest.pump.save()

        latest.delete()

        reversion.set_user(request.user)
        reversion.set_comment("Rollback refueling operation")

    messages.success(request, _("Refueling deleted"))
    return HttpResponseRedirect(reverse("fbomatic:index"))
