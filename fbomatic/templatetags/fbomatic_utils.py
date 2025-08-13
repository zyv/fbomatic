from django import template
from django.utils.translation import gettext as _

from fbomatic.models import Aircraft

register = template.Library()


@register.filter
def refueling_type(aircraft: Aircraft | None):
    return aircraft.registration if aircraft else _("Pump refilled")
