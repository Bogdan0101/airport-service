from datetime import datetime
from django.utils import timezone

from django.db.models import Count, F
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Airport, Route, Flight, Crew, AirplaneType, Airplane
from airport.serializers import FlightListSerializer
from django.core.cache import cache

FLIGHT_URL = reverse("airport:flights-list")


class FlightAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        list_queryset = (
            Flight.objects
            .select_related("route", "airplane", "route__source", "route__destination")
            .prefetch_related("crew")
            .annotate(
                tickets_available=(
                        F("airplane__rows") * F("airplane__seats_in_row")
                        - Count("tickets")
                )
            )
            .order_by("id")
        )
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airport1 = Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")
        self.airport2 = Airport.objects.create(name="Barcelona El Prat", closest_big_city="Barcelona")
        self.airport3 = Airport.objects.create(name="Warsaw Chopin", closest_big_city="Warsaw")
        self.route1 = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=2400,
        )
        self.route2 = Route.objects.create(
            source=self.airport3,
            destination=self.airport1,
            distance=800,
        )
        self.airplane_type1 = AirplaneType.objects.create(name="Boeing 737")
        self.airplane_type2 = AirplaneType.objects.create(name="Airbus A320")
        self.airplane1 = Airplane.objects.create(
            name="SkyBird-737",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type1,
        )
        self.airplane2 = Airplane.objects.create(
            name="AeroJet-A320",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type2,
        )
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe")
        self.crew2 = Crew.objects.create(first_name="Bob", last_name="Black")
        self.flight1 = Flight.objects.create(
            route=self.route1,
            airplane=self.airplane1,
            departure_time=timezone.make_aware(datetime(2025, 1, 12, 9, 0, 0)),
            arrival_time=timezone.make_aware(datetime(2025, 1, 12, 12, 30, 0)),
        )
        self.flight2 = Flight.objects.create(
            route=self.route2,
            airplane=self.airplane2,
            departure_time=timezone.make_aware(datetime(2025, 1, 13, 14, 0, 0)),
            arrival_time=timezone.make_aware(datetime(2025, 1, 13, 15, 30, 0)),
        )
        self.flight1.crew.add(self.crew1, self.crew2)
        self.flight2.crew.add(self.crew1, self.crew2)
        self.flight1_ser = FlightListSerializer(list_queryset.get(id=self.flight1.id)).data
        self.flights_ser = FlightListSerializer(list_queryset, many=True).data

    def test_str_for_flight(self):
        self.assertEqual(
            str(self.flight1),
            f"{self.flight1.route},"
            f" {self.flight1.airplane},"
            f" {self.flight1.departure_time},"
            f" {self.flight1.arrival_time}")

    def test_post_admin(self):
        data = {
            "route": self.route2.id,
            "airplane": self.airplane2.id,
            "departure_time": timezone.make_aware(datetime(2025, 1, 13, 14, 0, 0)),
            "arrival_time": timezone.make_aware(datetime(2025, 1, 13, 15, 30, 0)),
            "crew": [self.crew1.id, self.crew2.id],
        }
        res = self.client.post(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data_filter = {
            "route": self.route2,
            "airplane": self.airplane2,
            "departure_time": data["departure_time"],
            "arrival_time": data["arrival_time"],
        }
        self.assertTrue(Flight.objects.filter(**data_filter).exists())

    def test_get_with_filter_for_admin(self):
        data = {"departure_time": self.flight1.departure_time.strftime("%Y-%m-%d")}
        res = self.client.get(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.flight1_ser)
        data = {"departure_time": self.flight1.arrival_time.strftime("%Y-%m-%d")}
        res = self.client.get(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.flight1_ser)

    def test_get_admin(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.flights_ser)


class FlightAuthenticatedUserTests(TestCase):
    def setUp(self):
        cache.clear()
        list_queryset = (
            Flight.objects
            .select_related("route", "airplane", "route__source", "route__destination")
            .prefetch_related("crew")
            .annotate(
                tickets_available=(
                        F("airplane__rows") * F("airplane__seats_in_row")
                        - Count("tickets")
                )
            )
            .order_by("id")
        )
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airport1 = Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")
        self.airport2 = Airport.objects.create(name="Barcelona El Prat", closest_big_city="Barcelona")
        self.airport3 = Airport.objects.create(name="Warsaw Chopin", closest_big_city="Warsaw")
        self.route1 = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=2400,
        )
        self.route2 = Route.objects.create(
            source=self.airport3,
            destination=self.airport1,
            distance=800,
        )
        self.airplane_type1 = AirplaneType.objects.create(name="Boeing 737")
        self.airplane_type2 = AirplaneType.objects.create(name="Airbus A320")
        self.airplane1 = Airplane.objects.create(
            name="SkyBird-737",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type1,
        )
        self.airplane2 = Airplane.objects.create(
            name="AeroJet-A320",
            rows=30,
            seats_in_row=6,
            airplane_type=self.airplane_type2,
        )
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe")
        self.crew2 = Crew.objects.create(first_name="Bob", last_name="Black")
        self.flight1 = Flight.objects.create(
            route=self.route1,
            airplane=self.airplane1,
            departure_time=timezone.make_aware(datetime(2025, 1, 12, 9, 0, 0)),
            arrival_time=timezone.make_aware(datetime(2025, 1, 12, 12, 30, 0)),
        )
        self.flight2 = Flight.objects.create(
            route=self.route2,
            airplane=self.airplane2,
            departure_time=timezone.make_aware(datetime(2025, 1, 13, 14, 0, 0)),
            arrival_time=timezone.make_aware(datetime(2025, 1, 13, 15, 30, 0)),
        )
        self.flight1.crew.add(self.crew1, self.crew2)
        self.flight2.crew.add(self.crew1, self.crew2)
        self.flight1_ser = FlightListSerializer(list_queryset.get(id=self.flight1.id)).data
        self.flights_ser = FlightListSerializer(list_queryset, many=True).data

    def test_get_with_filter_for_user(self):
        data = {"departure_time": self.flight1.departure_time.strftime("%Y-%m-%d")}
        res = self.client.get(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.flight1_ser)
        data = {"departure_time": self.flight1.arrival_time.strftime("%Y-%m-%d")}
        res = self.client.get(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.flight1_ser)

    def test_post_authenticated_user(self):
        data = {
            "route": self.route2.id,
            "airplane": self.airplane2.id,
            "departure_time": timezone.make_aware(datetime(2025, 1, 13, 14, 0, 0)),
            "arrival_time": timezone.make_aware(datetime(2025, 1, 13, 15, 30, 0)),
            "crew": [self.crew1.id, self.crew2.id],
        }
        res = self.client.post(FLIGHT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_authenticated_user(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.flights_ser)


class FlightUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
