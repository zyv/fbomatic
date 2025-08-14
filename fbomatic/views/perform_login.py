import logging

from cuser.forms import AuthenticationForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fbomatic.vereinsflieger import VereinsfliegerApiSession

logger = logging.getLogger(__name__)
User = get_user_model()


def perform_login(request):
    def get_form():
        return AuthenticationForm(data=request.POST)

    form = get_form()
    if not form.is_valid():
        email, password = form.cleaned_data["email"], form.cleaned_data["password"]

        if email and password:
            email = email.lower()

            with VereinsfliegerApiSession(
                app_key=settings.VEREINSFLIEGER_APP_KEY,
                username=email,
                password=password,
            ) as vs:
                vf_user = vs.get_user()

            logger.warning(f"Importing/updating user from Vereinsflieger: {vf_user}")

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                User.objects.create_user(
                    email,
                    password,
                    first_name=vf_user.firstname,
                    last_name=vf_user.lastname,
                )
            else:
                user.set_password(password)
                user.first_name = vf_user.firstname
                user.last_name = vf_user.lastname
                user.save()

        form = get_form()
        if not form.is_valid():
            messages.error(request, _("Invalid form data"))

    login(request, form.get_user())
    return HttpResponseRedirect(reverse("fbomatic:index"))
