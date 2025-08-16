import pytest
from django.contrib.auth import get_user_model
from django.test import Client as DjangoTestClient

from fbomatic.models import Aircraft, Pump

User = get_user_model()

TEST_PASSWORD = "password123"


@pytest.fixture
def test_client() -> DjangoTestClient:
    return DjangoTestClient()


@pytest.fixture
def normal_user() -> User:
    return User.objects.create_user(
        email="user@example.com",
        password=TEST_PASSWORD,
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def staff_user() -> User:
    return User.objects.create_user(
        email="staff@example.com",
        password=TEST_PASSWORD,
        first_name="Staff",
        last_name="User",
        is_staff=True,
    )


@pytest.fixture
def db_pump() -> Pump:
    return Pump.objects.create(name="Test pump", capacity=1000, counter=50, remaining=500)


@pytest.fixture
def db_aircraft() -> Aircraft:
    return Aircraft.objects.create(registration="D-TEST")


def assert_message(response, level):
    assert len(response.context["messages"]) == 1
    assert list(response.context["messages"])[-1].level == level


def assert_last_redirect(response, url):
    assert response.redirect_chain[-1][0] == url
