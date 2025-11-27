from django.db import transaction
from rest_framework import serializers
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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew",)


class FlightRetrieveSerializer(FlightSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    route = RouteListSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
