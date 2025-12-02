import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer
from django.core.cache import cache

AIRPLANE_URL = reverse("airport:airplanes-list")


def image_upload_url(airplane_id):
    return reverse("airport:airplanes-upload-image", args=[airplane_id])


class AirplaneAdminTests(TestCase):
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
        self.airplane1_ser = AirplaneListSerializer(self.airplane1).data
        self.airplane2_ser = AirplaneListSerializer(self.airplane2).data
        self.airplanes = AirplaneListSerializer([self.airplane1, self.airplane2], many=True).data

    def tearDown(self):
        self.airplane1.image.delete()

    def test_upload_image_to_movie(self):
        url = image_upload_url(self.airplane1.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane1.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane1.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.airplane1.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_movie_list(self):
        url = AIRPLANE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "AeroJet-test",
                    "rows": 30,
                    "seats_in_row": 6,
                    "airplane_type": self.airplane_type1.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Airplane.objects.get(name="AeroJet-test")
        self.assertFalse(movie.image)

    def test_image_url_is_shown_on_movie_detail(self):
        url = image_upload_url(self.airplane1.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(reverse("airport:airplanes-detail", args=[self.airplane1.id]))
        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_movie_list(self):
        url = image_upload_url(self.airplane1.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)
        self.assertIn("image", res.data["results"][0].keys())

    def test_airplane_str(self):
        self.assertEqual(str(self.airplane1),
                         f"{self.airplane1.name}, {self.airplane1.rows}, {self.airplane1.seats_in_row}")

    def test_get_admin(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airplanes)

    def test_post_admin(self):
        data = {
            "name": "AeroJet-test",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type2.id,
        }
        res = self.client.post(AIRPLANE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Airplane.objects.filter(**data).exists())

    def test_get_with_filter_for_admin(self):
        data = {"name": self.airplane1.name}
        res = self.client.get(AIRPLANE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airplane1_ser)


class AirplaneAuthenticateUserTests(TestCase):
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
        self.airplane1_ser = AirplaneListSerializer(self.airplane1).data
        self.airplane2_ser = AirplaneListSerializer(self.airplane2).data
        self.airplanes = AirplaneListSerializer([self.airplane1, self.airplane2], many=True).data

    def test_get_with_filter_for_user(self):
        data = {"name": self.airplane1.name}
        res = self.client.get(AIRPLANE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.airplane1_ser)

    def test_get_authenticated_user(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.airplanes)

    def test_post_authenticated_user(self):
        data = {
            "name": "AeroJet-test",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type2.id,
        }
        res = self.client.post(AIRPLANE_URL, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AirplaneUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
