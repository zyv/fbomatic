from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache

User = get_user_model()


@never_cache
def health_check(_):
    users = User.objects.count()
    return JsonResponse(
        {
            "status": "pass",
            "checks": {
                "database:connectivity": [
                    {
                        "status": "pass",
                        "observedValue": users,
                        "time": timezone.now(),
                    }
                ]
            },
        }
    )
