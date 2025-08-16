import http.client

import pytest
from django.urls import reverse

from tests.views.conftest import TEST_PASSWORD, assert_last_redirect

pytestmark = pytest.mark.django_db


def test_logout_success_and_redirect_to_index(test_client, normal_user):
    assert test_client.login(email=normal_user.email, password=TEST_PASSWORD)

    response = test_client.post(
        reverse("fbomatic:logout"),
        data={"next": reverse("fbomatic:index")},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))

    page = response.content.decode()
    assert 'data-testid="button-log-in"' in page
    assert 'data-testid="button-log-out"' not in page


def test_logout_failure_requires_post(test_client):
    response = test_client.get(reverse("fbomatic:logout"))
    assert response.status_code == http.client.METHOD_NOT_ALLOWED
