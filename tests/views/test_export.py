import csv
import http.client
import io

import pytest
from django.contrib import messages
from django.urls import reverse

from fbomatic.models import Pump, Refueling
from fbomatic.templatetags.fbomatic_utils import refueling_type
from tests.conftest import assert_last_redirect, assert_message
from tests.views.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def test_export_success_staff_csv(test_client, staff_user, normal_user, db_pump, db_aircraft):
    other_pump = Pump.objects.create(name="Other pump", capacity=1000, counter=0, remaining=1000)

    records_main = [
        Refueling.objects.create(
            pump=db_pump,
            user=normal_user,
            aircraft=db_aircraft if i % 2 == 0 else None,
            counter=100 + i,
            quantity=10 + i,
        )
        for i in range(3)
    ]

    # Should NOT be included
    Refueling.objects.create(pump=other_pump, user=staff_user, aircraft=None, counter=999, quantity=1)

    assert test_client.login(email=staff_user.email, password=TEST_PASSWORD)
    response = test_client.post(reverse("fbomatic:export"), {"pump": db_pump.pk, "count": 2})

    assert response.status_code == http.client.OK
    assert response["Content-Type"].startswith("text/csv")

    reader = csv.reader(io.StringIO(response.content.decode()))

    head, *tail = list(reader)

    assert head == ["timestamp", "pump", "type", "counter", "quantity", "price", "email", "first_name", "last_name"]

    # Most recent first: records_main[2], records_main[1]
    for csv_row, record in zip(tail, list(reversed(records_main))[:2]):
        assert csv_row == [
            record.timestamp.isoformat(),
            record.pump.name,
            refueling_type(record.aircraft),
            str(record.counter),
            str(record.quantity),
            str(record.price) if record.price is not None else "",
            record.user.email,
            record.user.first_name,
            record.user.last_name,
        ]


def test_export_failure_form_data(test_client, staff_user):
    assert test_client.login(email=staff_user.email, password=TEST_PASSWORD)
    response = test_client.post(reverse("fbomatic:export"), {}, follow=True)
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)


def test_export_failure_authentication(test_client):
    url = reverse("fbomatic:export")
    response = test_client.post(url)
    assert response.status_code == http.client.FOUND
    assert response["Location"] == f"{reverse('fbomatic:index')}?next={url}"
