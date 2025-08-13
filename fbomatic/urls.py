from django.urls import path

from . import views

app_name = "fbomatic"
urlpatterns = (
    path("", views.index, name="index"),
    path("rollback/", views.rollback, name="rollback"),
    path("refuel/", views.refuel, name="refuel"),
    path("login/", views.perform_login, name="login"),
)
