from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
from django.core.cache import cache

AIRPLANE_TYPE_URL = reverse("airport:airplane_types-list")


class AirplaneTypeAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airplane_type1 = AirplaneType.objects.create(name="Boeing 737")
        self.airplane_type2 = AirplaneType.objects.create(name="Airbus A320")
        self.airplane_type1_ser = AirplaneTypeSerializer(self.airplane_type1).data
        self.airplane_type2_ser = AirplaneTypeSerializer(self.airplane_type2).data
        self.airplane_types_ser = AirplaneTypeSerializer([self.airplane_type1, self.airplane_type2], many=True).data

    def test_str_for_airplane_type(self):
        self.assertEqual(str(self.airplane_type1), f"{self.airplane_type1.name}")

    def test_post_admin(self):
        data = {"name": "test"}
        res = self.client.post(AIRPLANE_TYPE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AirplaneType.objects.filter(**data).exists())

    def test_get_admin(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airplane_types_ser)

    def test_get_with_filter_for_admin(self):
        data = {"name": self.airplane_type1.name}
        res = self.client.get(AIRPLANE_TYPE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airplane_type1_ser)


class AirplaneTypeAuthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airplane_type1 = AirplaneType.objects.create(name="Boeing 737")
        self.airplane_type2 = AirplaneType.objects.create(name="Airbus A320")
        self.airplane_type1_ser = AirplaneTypeSerializer(self.airplane_type1).data
        self.airplane_type2_ser = AirplaneTypeSerializer(self.airplane_type2).data
        self.airplane_types_ser = AirplaneTypeSerializer([self.airplane_type1, self.airplane_type2], many=True).data

    def test_get_with_filter_for_user(self):
        data = {"name": self.airplane_type1.name}
        res = self.client.get(AIRPLANE_TYPE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airplane_type1_ser)

    def test_get_authenticated_user(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airplane_types_ser)

    def test_post_authenticated_user(self):
        data = {"name": "test"}
        res = self.client.post(AIRPLANE_TYPE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AirplaneTypeUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
