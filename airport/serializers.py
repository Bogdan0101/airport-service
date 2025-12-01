from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Crew,
    Route,
    Airplane,
    AirplaneType,
    Flight,
    Order,
    Ticket,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class CrewFullNameSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("full_name",)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()


class AirplaneForAirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "capacity", "image",)
        read_only_fields = ("capacity",)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    airplanes = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = AirplaneType
        fields = ("id", "name", "airplanes",)


class AirplaneTypeRetrieveSerializer(AirplaneTypeSerializer):
    airplanes = AirplaneForAirplaneTypeSerializer(many=True, read_only=True)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "capacity", "airplane_type", "image",)
        read_only_fields = ("capacity",)


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(slug_field="name", read_only=True)


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ("id", "rows", "seats_in_row", "capacity", "airplane_type", "image",)


class FlightSerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    source = serializers.CharField(source="route.source.name", read_only=True)
    destination = serializers.CharField(source="route.destination.name", read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )


class FlightRetrieveSerializer(FlightSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "route",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket

        fields = ("id", "row", "seat", "flight")


class FlightForTicketSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "source", "destination", "departure_time", "arrival_time",)


class TicketListSerializer(TicketSerializer):
    flight = FlightForTicketSerializer(read_only=True, many=False)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
