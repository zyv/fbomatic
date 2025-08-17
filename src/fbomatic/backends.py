import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from fbomatic.vereinsflieger import VereinsfliegerApiSession, VereinsfliegerError

User = get_user_model()
logger = logging.getLogger(__name__)


class VereinsfliegerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is not None:
            return user

        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        logger.info(f"Trying to authenticate against Vereinsflieger: {username}")

        # Normalize emails sent to Vereinsflieger
        username = username.lower()

        try:
            with VereinsfliegerApiSession(
                app_key=settings.VEREINSFLIEGER_APP_KEY,
                username=username,
                password=password,
            ) as vs:
                vf_user = vs.get_user()
        except VereinsfliegerError:
            return None
        else:
            logger.warning(f"Importing/updating user from Vereinsflieger: {vf_user}")
            user, _ = User.objects.update_or_create(
                email=username,
                defaults={
                    "first_name": vf_user.firstname,
                    "last_name": vf_user.lastname,
                },
            )
            user.set_password(password)
            user.save()

            return user
