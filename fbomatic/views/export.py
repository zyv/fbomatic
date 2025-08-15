import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from fbomatic.forms import ExportForm
from fbomatic.models import Refueling
from fbomatic.templatetags.fbomatic_utils import refueling_type


@staff_member_required(login_url=reverse_lazy("fbomatic:index"))
def export(request):
    form = ExportForm(request.POST)

    if not form.is_valid():
        messages.error(request, _("Invalid form data"))
        return HttpResponseRedirect(reverse("fbomatic:index"))

    refueling = Refueling.objects.filter(pump=form.cleaned_data["pump"]).order_by("-timestamp")[
        : form.cleaned_data["count"]
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="refueling-{timezone.now().date().isoformat()}.csv"'

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
