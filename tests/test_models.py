import pytest

from fbomatic.models import Aircraft

pytestmark = pytest.mark.django_db


def test_aircraft():
    for priority, registration in zip((1, 2, 1), ("A", "B", "C")):
        Aircraft.objects.create(registration=registration, priority=priority)

    a1, a2, a3 = Aircraft.objects.all()

    assert a1.registration == "B"
    assert a2.registration == "A"
    assert a3.registration == "C"
