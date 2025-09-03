from django.conf import settings


def global_settings(_):
    return {
        "PROJECT_VERSION": settings.PROJECT_VERSION,
    }
