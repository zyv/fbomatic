import pytest
from django.contrib import messages
from django.urls import reverse

from fbomatic.models import Refueling
from tests.conftest import assert_last_redirect, assert_message
from tests.views.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("owner_fixture", "actor_fixture"),
    [
        ("normal_user", "staff_user"),
        ("normal_user", "normal_user"),
    ],
)
def test_rollback_latest_success(owner_fixture, actor_fixture, request, test_client, db_pump):
    actor_user = request.getfixturevalue(actor_fixture)
    owner_user = request.getfixturevalue(owner_fixture)

    previous_remaining, previous_counter = db_pump.remaining, db_pump.counter

    record = Refueling.objects.create(
        pump=db_pump,
        user=owner_user,
        aircraft=None,
        counter=db_pump.counter,
        quantity=10,
    )

    assert test_client.login(email=actor_user.email, password=TEST_PASSWORD)
    response = test_client.post(reverse("fbomatic:rollback"), follow=True)
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.SUCCESS)

    assert Refueling.objects.count() == 0

    db_pump.refresh_from_db()
    assert db_pump.remaining == previous_remaining + record.quantity
    assert db_pump.counter == previous_counter - record.quantity


def test_rollback_latest_failure(test_client, db_pump, staff_user, normal_user):
    Refueling.objects.create(
        pump=db_pump,
        user=staff_user,
        counter=db_pump.counter,
        quantity=10,
    )

    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)
    response = test_client.post(reverse("fbomatic:rollback"), follow=True)
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)

    assert Refueling.objects.count() == 1
