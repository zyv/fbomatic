import logging

from cuser.forms import AuthenticationForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from fbomatic.vereinsflieger import VereinsfliegerApiSession, VereinsfliegerError

logger = logging.getLogger(__name__)
User = get_user_model()


def perform_login(request):
    # First attempt
    form = AuthenticationForm(data=request.POST)

    if form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse("fbomatic:index"))

    # Try to import/update user from Vereinsflieger
    email, password = form.cleaned_data.get("email"), form.cleaned_data.get("password")

    if not email or not password:
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    email = email.lower()

    try:
        with VereinsfliegerApiSession(
            app_key=settings.VEREINSFLIEGER_APP_KEY,
            username=email,
            password=password,
        ) as vs:
            vf_user = vs.get_user()
    except VereinsfliegerError:
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    logger.warning(f"Importing/updating user from Vereinsflieger: {vf_user}")

    user, _created = User.objects.get_or_create(email=email)
    user.set_password(password)
    user.first_name = vf_user.firstname
    user.last_name = vf_user.lastname
    user.save()

    # Second attempt
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
    else:
        messages.error(request, _("Invalid form data"))

    return HttpResponseRedirect(reverse("fbomatic:index"))
