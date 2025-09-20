from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q

User = get_user_model()

User.__str__ = lambda self: f"{self.first_name} {self.last_name} ({self.email})"


class Aircraft(models.Model):
    registration = models.CharField(max_length=16, unique=True)
    priority = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return self.registration

    class Meta:
        ordering = ("-priority", "registration")
        verbose_name_plural = "aircraft"


class Pump(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(validators=(MinValueValidator(1),))
    counter = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        constraints = (CheckConstraint(condition=Q(remaining__lte=F("capacity")), name="remaining_lte_capacity"),)


class Refueling(models.Model):
    pump = models.ForeignKey(Pump, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    aircraft = models.ForeignKey(Aircraft, blank=True, null=True, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    counter = models.PositiveIntegerField()
    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("1"))],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Refueling(timestamp={self.timestamp.date().isoformat()}, user={self.user})"

    class Meta:
        ordering = ("-timestamp",)
        constraints = (
            CheckConstraint(
                condition=Q(price__isnull=True) | (Q(aircraft__isnull=True) & Q(quantity__lt=0)), name="give_or_take"
            ),
        )
