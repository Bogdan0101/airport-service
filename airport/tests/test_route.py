from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Route, Airport
from airport.serializers import RouteListSerializer, AirportSerializer

ROUTE_URL = reverse("airport:routes-list")


class RouteAdminTests(TestCase):
    def setUp(self):
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
        self.route_serializer1 = RouteListSerializer(self.route1).data
        self.route_serializer2 = RouteListSerializer(self.route2).data
        self.routes_serializer = RouteListSerializer([self.route1, self.route2], many=True).data

    def test_str_for_route(self):
        self.assertEqual(str(self.route1), f"{self.route1.source} > {self.route1.destination}")

    def test_get_admin(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.routes_serializer)

    def test_get_with_filter_for_admin(self):
        filter_by_source = {
            "source": self.airport1.name,
        }
        res = self.client.get(ROUTE_URL, filter_by_source)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(res.data["results"][0], self.route_serializer1)
        filter_by_destination = {
            "destination": self.airport2.name,
        }
        res = self.client.get(ROUTE_URL, filter_by_destination)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(res.data["results"][0], self.route_serializer1)

    def test_post_admin(self):
        data = {
            "source": self.airport3.id,
            "destination": self.airport2.id,
            "distance": 1200,
        }
        res = self.client.post(ROUTE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Route.objects.filter(**data).exists())


class RouteAuthenticatedUserTests(TestCase):
    def setUp(self):
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
        self.route_serializer1 = RouteListSerializer(self.route1).data
        self.route_serializer2 = RouteListSerializer(self.route2).data
        self.routes_serializer = RouteListSerializer([self.route1, self.route2], many=True).data

    def test_get_with_filter_for_user(self):
        filter_by_source = {
            "source": self.airport1.name,
        }
        res = self.client.get(ROUTE_URL, filter_by_source)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(res.data["results"][0], self.route_serializer1)
        filter_by_destination = {
            "destination": self.airport2.name,
        }
        res = self.client.get(ROUTE_URL, filter_by_destination)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(res.data["results"]))
        self.assertEqual(res.data["results"][0], self.route_serializer1)

    def test_get_authenticated_user(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))

    def test_post_authenticated_user(self):
        data = {
            "source": self.airport3,
            "destination": self.airport2,
            "distance": 1200,
        }
        res = self.client.post(ROUTE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RouteUnauthenticateUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
