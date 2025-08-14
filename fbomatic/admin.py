import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from fbomatic.models import Aircraft, Pump, Refueling
from fbomatic.templatetags.fbomatic_utils import refueling_type

FUELING_RECORDS_LIMIT = 500


@admin.register(Aircraft)
class AircraftAdmin(VersionAdmin):
    pass


@admin.action(description=_("Download last {count} refueling records").format(count=FUELING_RECORDS_LIMIT))
def download_records(self, request, queryset):
    refueling = Refueling.objects.filter(pump__in=queryset).order_by("-timestamp")[:FUELING_RECORDS_LIMIT]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="refueling-{timezone.now().date().isoformat()}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ("timestamp", "type", "counter", "remaining", "quantity", "price", "email", "first_name", "last_name")
    )
    for record in refueling:
        writer.writerow(
            (
                record.timestamp.isoformat(),
                refueling_type(record.aircraft),
                record.counter,
                record.remaining,
                record.quantity,
                record.price,
                record.user.email,
                record.user.first_name,
                record.user.last_name,
            )
        )

    return response


@admin.register(Pump)
class PumpAdmin(VersionAdmin):
    list_display = ("name", "capacity", "counter", "remaining")
    actions = (download_records,)


@admin.register(Refueling)
class RefuelingAdmin(VersionAdmin):
    list_display = ("timestamp", "user", "aircraft", "quantity", "counter", "remaining")
