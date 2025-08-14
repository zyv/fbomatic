from django.urls import path

from fbomatic.views.index import index
from fbomatic.views.perform_login import perform_login
from fbomatic.views.refuel import refuel
from fbomatic.views.rollback import rollback
from fbomatic.views.top_up import top_up

app_name = "fbomatic"
urlpatterns = (
    path("", index, name="index"),
    path("rollback/", rollback, name="rollback"),
    path("refuel/", refuel, name="refuel"),
    path("top-up/", top_up, name="top-up"),
    path("login/", perform_login, name="login"),
)
