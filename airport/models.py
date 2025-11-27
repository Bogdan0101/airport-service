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

class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=100)

class Route(models.Model):
    source = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="routes_to")
    distance = models.IntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination cannot be the same.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (f"{slugify(instance.name)}-{uuid.uuid4()}"
                + pathlib.Path(filename).suffix)
    return pathlib.Path("upload-image/") / pathlib.Path(filename)

class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey("AirplaneType", on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to=airplane_image_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Flight(models.Model):
    route = models.ForeignKey("Route", on_delete=models.CASCADE)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)

