from unittest.mock import MagicMock

import pytest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse

from fbomatic.vereinsflieger import VereinsfliegerError, VereinsfliegerUser
from tests.conftest import assert_last_redirect, assert_message

pytestmark = pytest.mark.django_db

User = get_user_model()


def test_perform_login_failure(test_client, monkeypatch):
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


def test_perform_login_success(test_client, monkeypatch):
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
    assert not len(response.context["messages"])

    assert User.objects.count() == 1

    assert not test_client.login(email="foo@bar.quux", password="bad_password")
    assert test_client.login(email="foo@bar.quux", password="good_password")
