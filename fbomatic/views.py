import logging
from dataclasses import asdict, dataclass

import reversion
from cuser.forms import AuthenticationForm
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fbomatic.forms import FuelingForm
from fbomatic.models import Pump, Refueling
from fbomatic.vereinsflieger import VereinsfliegerApiSession

REFUELING_RECORDS_LIMIT = 10

logger = logging.getLogger(__name__)
User = get_user_model()


def index(request):
    @dataclass(frozen=True, kw_only=True)
    class Context:
        pump: Pump
        auth_form: forms.Form
        fueling_form: forms.Form
        refueling_actions: QuerySet[Refueling]
        actions_caption: str
        refueling_threshold: int

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
                    fueling_form=FuelingForm(),
                    refueling_actions=refueling_actions,
                    actions_caption=_("Last {count} fueling actions").format(count=REFUELING_RECORDS_LIMIT),
                    refueling_threshold=settings.REFUELING_THRESHOLD_LITERS,
                )
            )
        ),
    )


def perform_login(request):
    def get_form():
        return AuthenticationForm(data=request.POST)

    form = get_form()
    if not form.is_valid():
        email, password = form.cleaned_data["email"], form.cleaned_data["password"]

        if email and password:
            email = email.lower()

            with VereinsfliegerApiSession(
                app_key=settings.VEREINSFLIEGER_APP_KEY,
                username=email,
                password=password,
            ) as vs:
                vf_user = vs.get_user()

            logger.warning(f"Importing/updating user from Vereinsflieger: {vf_user}")

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                User.objects.create_user(
                    email,
                    password,
                    first_name=vf_user.firstname,
                    last_name=vf_user.lastname,
                )
            else:
                user.set_password(password)
                user.first_name = vf_user.firstname
                user.last_name = vf_user.lastname
                user.save()

        form = get_form()
        if not form.is_valid():
            messages.error(request, _("Invalid form data"))

    login(request, form.get_user())
    return HttpResponseRedirect(reverse("fbomatic:index"))


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

            Refueling.objects.create(
                pump=pump,
                user=request.user,
                aircraft=form.cleaned_data["aircraft"],
                counter=pump.counter,
                remaining=pump.remaining,
                quantity=quantity,
            )

            reversion.set_user(request.user)
            reversion.set_comment("Refueling operation")

            # TODO mail

    messages.success(request, _("Refueling recorded"))
    return HttpResponseRedirect(reverse("fbomatic:index"))


@login_required
def rollback(request):
    with transaction.atomic():
        latest = Refueling.objects.first()

        if latest is None or latest.user != request.user:
            messages.error(request, _("Refueling deletion failed"))
            return HttpResponseRedirect(reverse("fbomatic:index"))

        with reversion.create_revision():
            Pump.objects.filter(pk=latest.pump.pk).update(
                remaining=F("remaining") + latest.quantity,
                counter=F("counter") - latest.quantity,
            )

            latest.delete()

            reversion.set_user(request.user)
            reversion.set_comment("Rollback refueling operation")

    messages.success(request, _("Refueling deleted"))
    return HttpResponseRedirect(reverse("fbomatic:index"))


@staff_member_required
def top_up(request):
    with transaction.atomic():
        pump = Pump.objects.first()

        if pump is None or pump.remaining == pump.capacity or Pump.objects.count() > 1:
            messages.error(request, _("Pump level reset failed"))
            return HttpResponseRedirect(reverse("fbomatic:index"))

        quantity = pump.remaining - pump.capacity

        with reversion.create_revision():
            Refueling.objects.create(
                pump=pump,
                user=request.user,
                aircraft=None,
                counter=pump.counter,
                remaining=pump.capacity,
                quantity=quantity,
            )

            pump.remaining = pump.capacity
            pump.save()

            reversion.set_user(request.user)
            reversion.set_comment("Pump level reset")

            # TODO mail

    messages.success(request, _("Pump level reset to full"))
    return HttpResponseRedirect(reverse("fbomatic:index"))
