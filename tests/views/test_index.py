import http.client

import pytest
from django.urls import reverse

from fbomatic.models import Refueling
from tests.views.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db


def test_index_success_anonymous(test_client):
    response = test_client.get(reverse("fbomatic:index"))
    assert response.status_code == http.client.OK
    assert 'data-testid="button-log-in"' in response.content.decode()


def test_index_success_authorized(test_client, normal_user, staff_user, db_pump, db_aircraft):
    for i in range(14):
        Refueling.objects.create(
            pump=db_pump,
            user=normal_user if i % 2 else staff_user,
            aircraft=db_aircraft,
            counter=i * 10,
            quantity=10,
        )

    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)
    response = test_client.get(reverse("fbomatic:index"))
    assert response.status_code == http.client.OK

    response_string = response.content.decode()
    assert 'data-testid="button-log-in"' not in response.content.decode()
    assert 'data-testid="button-record-fueling"' in response_string
    assert 'data-testid="button-rollback"' in response_string
    assert 'data-testid="button-record-top-up"' in response_string
    assert 'data-testid="button-export"' not in response_string
    assert 'data-testid="button-administration"' not in response_string
    assert 'data-testid="button-log-out"' in response_string
