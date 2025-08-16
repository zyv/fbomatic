import logging

from cuser.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

logger = logging.getLogger(__name__)
User = get_user_model()


@never_cache
@csrf_protect
@sensitive_post_parameters()
def perform_login(request):
    form = AuthenticationForm(data=request.POST)

    if form.is_valid():
        login(request, form.get_user())
        messages.success(request, _("Welcome,") + f" {request.user.first_name}!")
    else:
        messages.error(request, _("Invalid form data"))

    return HttpResponseRedirect(reverse("fbomatic:index"))
