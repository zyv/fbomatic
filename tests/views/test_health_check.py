import http.client
import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_health_check_success_json_payload(test_client, monkeypatch):
    mock_timezone = MagicMock()
    mock_timezone.now.return_value = datetime.fromisoformat("2025-08-25T14:58:34.206Z")
    monkeypatch.setattr("fbomatic.views.health_check.timezone", mock_timezone)

    response = test_client.get(reverse("fbomatic:health-check"))
    assert response.status_code == http.client.OK
    assert response["Content-Type"] == "application/json"

    expected = json.loads("""
{
  "status": "pass",
  "checks": {
    "database:connectivity": [
      {
        "status": "pass",
        "observedValue": 0,
        "time": "2025-08-25T14:58:34.206Z"
      }
    ]
  }
}
""")

    assert response.json() == expected


def test_health_check_never_cache_headers(test_client):
    response = test_client.get(reverse("fbomatic:health-check"))

    cache_control = response.get("Cache-Control", "")
    assert "no-cache" in cache_control
    assert "no-store" in cache_control
    assert "max-age=0" in cache_control
