from django.contrib import admin
from reversion.admin import VersionAdmin

from fbomatic.models import Aircraft, Pump, Refueling


@admin.register(Aircraft)
class AircraftAdmin(VersionAdmin):
    pass


@admin.register(Pump)
class PumpAdmin(VersionAdmin):
    list_display = ("name", "capacity", "counter", "remaining")


@admin.register(Refueling)
class RefuelingAdmin(VersionAdmin):
    list_display = ("timestamp", "pump", "user", "aircraft", "quantity", "counter", "price")
