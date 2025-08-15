import pytest
from django.contrib import messages
from django.core import mail
from django.urls import reverse

from fbomatic.models import Refueling
from tests.conftest import assert_last_redirect, assert_message
from tests.views.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def test_refuel_success_no_mail(test_client, db_pump, db_aircraft, settings, normal_user):
    settings.REFUELING_THRESHOLD_LITERS = db_pump.remaining + 100

    previous_remaining, previous_counter = db_pump.remaining, db_pump.counter

    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)
    response = test_client.post(
        reverse("fbomatic:refuel"),
        data={"aircraft": db_aircraft.id, "quantity": 10},
        follow=True,
    )

    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.SUCCESS)

    db_pump.refresh_from_db()
    assert db_pump.remaining == previous_remaining - 10
    assert db_pump.counter == previous_counter + 10

    record = Refueling.objects.first()
    assert record.pump == db_pump
    assert record.user == normal_user
    assert record.aircraft == db_aircraft
    assert record.counter == db_pump.counter
    assert record.quantity == 10

    assert len(mail.outbox) == 0


def test_refuel_success_and_email_sent(test_client, db_pump, db_aircraft, settings, normal_user):
    settings.REFUELING_THRESHOLD_LITERS = db_pump.remaining

    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)
    test_client.post(reverse("fbomatic:refuel"), data={"aircraft": db_aircraft.id, "quantity": 10}, follow=True)

    assert len(mail.outbox) == 1


def test_refuel_failure_form_data(test_client, db_pump, db_aircraft, normal_user):
    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)
    response = test_client.post(
        reverse("fbomatic:refuel"),
        data={"aircraft": db_aircraft.id, "quantity": -4},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)
