import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from fbomatic.forms import ExportForm
from fbomatic.models import Refueling
from fbomatic.templatetags.fbomatic_utils import refueling_type


@never_cache
@csrf_protect
@staff_member_required(login_url=reverse_lazy("fbomatic:index"))
def export(request):
    form = ExportForm(request.POST)

    if not form.is_valid():
        messages.error(request, form.get_custom_error_message())
        return HttpResponseRedirect(reverse("fbomatic:index"))

    pump, count = form.cleaned_data["pump"], form.cleaned_data["count"]
    refueling = Refueling.objects.filter(pump=pump).order_by("-timestamp")[:count]

    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; "
            f'filename="refueling-{pump.name.lower()}-{timezone.now().date().isoformat()}.csv"'
        },
    )

    writer = csv.writer(response)
    writer.writerow(("timestamp", "pump", "type", "counter", "quantity", "price", "email", "first_name", "last_name"))
    for record in refueling:
        writer.writerow(
            (
                record.timestamp.isoformat(),
                record.pump.name,
                refueling_type(record.aircraft),
                record.counter,
                record.quantity,
                record.price,
                record.user.email,
                record.user.first_name,
                record.user.last_name,
            )
        )

    return response
