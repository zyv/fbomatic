from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Aircraft(models.Model):
    registration = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.registration

    class Meta:
        ordering = ("registration",)
        verbose_name_plural = "aircraft"


class Pump(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(validators=(MinValueValidator(1),))
    counter = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Refueling(models.Model):
    pump = models.ForeignKey(Pump, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    aircraft = models.ForeignKey(Aircraft, blank=True, null=True, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    counter = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"Refueling(timestamp={self.timestamp.date().isoformat()}, user={self.user})"

    class Meta:
        ordering = ("-timestamp",)
