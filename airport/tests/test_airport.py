from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Airport
from airport.serializers import AirportSerializer
from django.core.cache import cache

AIRPORT_URL = reverse("airport:airports-list")


class AirportAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airport1 = Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")
        self.airport2 = Airport.objects.create(name="Barcelona El Prat", closest_big_city="Barcelona")
        self.airport1_serializer = AirportSerializer(self.airport1).data
        self.airport2_serializer = AirportSerializer(self.airport2).data
        self.airports_serializer = AirportSerializer([self.airport1, self.airport2], many=True).data

    def test_str_for_airport(self):
        self.assertEqual(str(self.airport1), f"{self.airport1.name}")

    def test_post_admin(self):
        data = {"name": "test", "closest_big_city": "test1"}
        res = self.client.post(AIRPORT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Airport.objects.filter(**data).exists())

    def test_get_admin(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airports_serializer)

    def test_get_with_filter_for_admin(self):
        filter_data = {
            "name": self.airport1.name,
        }
        res = self.client.get(AIRPORT_URL, filter_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airport1_serializer)
        self.assertNotEqual(res.data["results"][0], self.airport2_serializer)


class AirportAuthenticatedUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airport1 = Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")
        self.airport2 = Airport.objects.create(name="Barcelona El Prat", closest_big_city="Barcelona")
        self.airport1_serializer = AirportSerializer(self.airport1).data
        self.airport2_serializer = AirportSerializer(self.airport2).data
        self.airports_serializer = AirportSerializer([self.airport1, self.airport2], many=True).data

    def test_get_with_filter_for_user(self):
        filter_data = {
            "name": self.airport1.name,
        }
        res = self.client.get(AIRPORT_URL, filter_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airport1_serializer)
        self.assertNotEqual(res.data["results"][0], self.airport2_serializer)

    def test_get_authenticated_user(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airports_serializer)

    def test_post_authenticated_user(self):
        data = {"name": "test", "closest_big_city": "test1"}
        res = self.client.post(AIRPORT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AirportUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
