from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Crew
from airport.serializers import CrewSerializer
from django.core.cache import cache

CREW_URL = reverse("airport:crew-list")


class CrewAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_superuser(
            email="admin123@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe")
        self.crew2 = Crew.objects.create(first_name="Bob", last_name="Black")
        self.crew1_serializer = CrewSerializer(self.crew1).data
        self.crew2_serializer = CrewSerializer(self.crew2).data
        self.crew_all_serializer = CrewSerializer([self.crew1, self.crew2], many=True).data

    def test_str_for_crew(self):
        self.assertEqual(str(self.crew1), f"{self.crew1.first_name} {self.crew1.last_name}")

    def test_full_name_for_crew(self):
        self.assertEqual(self.crew2.full_name, f"{self.crew2.first_name} {self.crew2.last_name}")

    def test_post_admin(self):
        data = {"first_name": "test", "last_name": "test1"}
        res = self.client.post(CREW_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Crew.objects.filter(**data).exists())

    def test_get_admin(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.crew_all_serializer)

    def test_get_with_filter_for_admin(self):
        filter_data = {
            "first_name": self.crew1.first_name,
            "last_name": self.crew1.last_name,
        }
        res = self.client.get(CREW_URL, filter_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        self.assertEqual(res.data["results"][0], self.crew1_serializer)
        self.assertNotEqual(res.data["results"][0], self.crew2_serializer)


class CrewAuthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe")
        self.crew2 = Crew.objects.create(first_name="Bob", last_name="Black")
        self.crew1_serializer = CrewSerializer(self.crew1).data
        self.crew2_serializer = CrewSerializer(self.crew2).data
        self.crew_all_serializer = CrewSerializer([self.crew1, self.crew2], many=True).data

    def test_get_with_filter_for_user(self):
        filter_data = {
            "first_name": self.crew1.first_name,
            "last_name": self.crew1.last_name,
        }
        res = self.client.get(CREW_URL, filter_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        self.assertEqual(res.data["results"][0], self.crew1_serializer)
        self.assertNotEqual(res.data["results"][0], self.crew2_serializer)

    def test_get_authenticated_user(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.crew_all_serializer)

    def test_post_authenticated_user(self):
        data = {"first_name": "test", "last_name": "test1"}
        res = self.client.post(CREW_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class CrewUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
