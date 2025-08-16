from decimal import Decimal

import pytest
from django.contrib import messages
from django.core import mail
from django.urls import reverse

from fbomatic.models import Refueling
from tests.views.conftest import TEST_PASSWORD, assert_last_redirect, assert_message

pytestmark = pytest.mark.django_db


def test_top_up_success(test_client, db_pump, staff_user):
    counter_before_top_up, remaining_before_top_up = db_pump.counter, db_pump.remaining

    assert test_client.login(email=staff_user.email, password=TEST_PASSWORD)
    response = test_client.post(
        reverse("fbomatic:top-up"),
        data={"pump": db_pump.id, "quantity": 100, "price": Decimal("2.000")},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.SUCCESS)

    db_pump.refresh_from_db()
    assert db_pump.remaining == remaining_before_top_up + 100
    assert db_pump.counter == counter_before_top_up

    record = Refueling.objects.first()
    assert record.pump == db_pump
    assert record.user == staff_user
    assert record.aircraft is None
    assert record.counter == counter_before_top_up
    assert record.quantity == -100
    assert record.price == Decimal("2.000")

    assert len(mail.outbox) == 1


def test_top_up_failure_authentication(test_client, db_pump):
    response = test_client.post(
        reverse("fbomatic:top-up"),
        data={"pump": db_pump.id, "quantity": 100, "price": Decimal("2.000")},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))


def test_top_up_failure_capacity(test_client, db_pump, staff_user):
    assert test_client.login(email=staff_user.email, password=TEST_PASSWORD)
    response = test_client.post(
        reverse("fbomatic:top-up"),
        data={"pump": db_pump.id, "quantity": 2000, "price": Decimal("2.000")},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)


def test_top_up_failure_form_data(test_client, db_pump, staff_user):
    assert test_client.login(email=staff_user.email, password=TEST_PASSWORD)
    response = test_client.post(
        reverse("fbomatic:top-up"),
        data={"pump": db_pump.id, "quantity": -10, "price": Decimal("0.123")},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)
