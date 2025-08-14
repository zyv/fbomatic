import pytest


@pytest.fixture(autouse=True)
def _django_override_settings_staticfiles_storage(settings):
    settings.STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"


def assert_message(response, level):
    assert len(response.context["messages"]) == 1
    assert list(response.context["messages"])[-1].level == level


def assert_last_redirect(response, url):
    assert response.redirect_chain[-1][0] == url
