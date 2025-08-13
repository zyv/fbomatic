import logging
from dataclasses import asdict, dataclass

import reversion
from cuser.forms import AuthenticationForm
from django import forms
from django.conf import settings
from django.contrib import messages
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

    pump = Pump.objects.first()
    quantity = form.cleaned_data["quantity"]

    if pump.remaining < quantity:
        messages.error(request, _("Not enough fuel in the pump"))
    else:
        # TODO mail

        with transaction.atomic(), reversion.create_revision():
            Pump.objects.filter(pk=pump.pk).update(remaining=F("remaining") - quantity, counter=F("counter") + quantity)
            pump.refresh_from_db()

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

        messages.success(request, _("Refueling recorded"))

    return HttpResponseRedirect(reverse("fbomatic:index"))
