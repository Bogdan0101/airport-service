import pathlib
import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        "Airport",
        on_delete=models.CASCADE,
        related_name="routes_from")
    destination = models.ForeignKey(
        "Airport",
        on_delete=models.CASCADE,
        related_name="routes_to")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} > {self.destination}"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination cannot be the same.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (f"{slugify(instance.name)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path("upload-image/") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType",
        on_delete=models.CASCADE,
        related_name="airplanes")
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=airplane_image_path)

    def __str__(self):
        return f"{self.name}, {self.rows}, {self.seats_in_row}"

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Flight(models.Model):
    route = models.ForeignKey("Route", on_delete=models.CASCADE)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    def __str__(self):
        return (f"{self.route}"
                f", {self.airplane}"
                f", {self.departure_time}"
                f", {self.arrival_time}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders")

    def __str__(self):
        return f"{self.created_at}, {self.user}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        "Flight",
        on_delete=models.CASCADE,
        related_name="tickets")
    order = models.ForeignKey("Order",
                              on_delete=models.CASCADE,
                              related_name="tickets")

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(self,
             *args,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.row}, {self.seat}, {self.flight}, {self.order}"

    class Meta:
        unique_together = ("row", "seat", "flight")
        ordering = ["row", "seat"]
