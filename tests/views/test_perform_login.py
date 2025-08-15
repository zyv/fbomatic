from unittest.mock import MagicMock

import pytest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse

from fbomatic.vereinsflieger import VereinsfliegerError, VereinsfliegerUser
from tests.conftest import assert_last_redirect, assert_message
from tests.views.conftest import TEST_PASSWORD

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_perform_login_success_local(test_client, db_pump, db_aircraft, normal_user):
    response = test_client.post(
        reverse("fbomatic:login"),
        data={"email": normal_user.email, "password": TEST_PASSWORD},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.SUCCESS)


def test_perform_login_failure_vereinsflieger(test_client, monkeypatch):
    assert not test_client.login(email="foo@bar.quux", password="good_password")

    mock_vf_session = MagicMock()
    mock_vf_session.return_value.__enter__.return_value = mock_vf_session
    mock_vf_session.get_user.side_effect = VereinsfliegerError
    monkeypatch.setattr("fbomatic.views.perform_login.VereinsfliegerApiSession", mock_vf_session)

    response = test_client.post(
        reverse("fbomatic:login"),
        data={"email": "foo@bar.quux", "password": "good_password"},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)

    assert not User.objects.count()
    assert not test_client.login(email="foo@bar.quux", password="good_password")


def test_perform_login_success_vereinsflieger(test_client, monkeypatch):
    assert not test_client.login(email="foo@bar.quux", password="good_password")

    mock_vf_session = MagicMock()
    mock_vf_session.return_value.__enter__.return_value = mock_vf_session
    mock_vf_session.get_user.return_value = VereinsfliegerUser(
        uid="123",
        firstname="Foo",
        lastname="Bar",
        email="foo@bar.quux",
    )
    monkeypatch.setattr("fbomatic.views.perform_login.VereinsfliegerApiSession", mock_vf_session)

    response = test_client.post(
        reverse("fbomatic:login"),
        data={"email": "foo@bar.quux", "password": "good_password"},
        follow=True,
    )
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.SUCCESS)

    assert User.objects.count() == 1

    assert not test_client.login(email="foo@bar.quux", password="bad_password")
    assert test_client.login(email="foo@bar.quux", password="good_password")


def test_perform_login_failure_form_data(test_client, db_pump, db_aircraft):
    response = test_client.post(reverse("fbomatic:login"), data={}, follow=True)
    assert_last_redirect(response, reverse("fbomatic:index"))
    assert_message(response, messages.ERROR)
