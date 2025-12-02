from datetime import datetime
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport.models import Ticket, Order, AirplaneType, Airplane, Airport, Route, Flight
from airport.serializers import OrderListSerializer
from django.core.cache import cache

ORDER_URL = reverse("airport:orders-list")


class OrderAuthenticatedUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.airplane_type1 = AirplaneType.objects.create(name="Boeing 737")
        self.airplane1 = Airplane.objects.create(
            name="SkyBird-737",
            rows=25,
            seats_in_row=6,
            airplane_type=self.airplane_type1,
        )
        self.airport1 = Airport.objects.create(name="Kyiv Boryspil", closest_big_city="Kyiv")
        self.airport2 = Airport.objects.create(name="Barcelona El Prat", closest_big_city="Barcelona")
        self.route1 = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=2400,
        )
        self.flight1 = Flight.objects.create(
            route=self.route1,
            airplane=self.airplane1,
            departure_time=timezone.make_aware(datetime(2025, 1, 12, 9, 0, 0)),
            arrival_time=timezone.make_aware(datetime(2025, 1, 12, 12, 30, 0)),
        )

    def test_create_order_with_tickets(self):
        data = {
            "tickets": [
                {"row": 2, "seat": 3, "flight": self.flight1.id},
                {"row": 2, "seat": 4, "flight": self.flight1.id}
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 2)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        tickets = order.tickets.all()
        self.assertEqual(tickets[0].order.id, order.id)
        self.assertEqual(tickets[1].order.id, order.id)
        self.assertEqual(tickets[0].row, 2)
        self.assertEqual(tickets[0].seat, 3)
        self.assertEqual(tickets[1].row, 2)
        self.assertEqual(tickets[1].seat, 4)

    def test_create_order_without_tickets(self):
        data = {"tickets": []}
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_buy_ticket_that_is_occupied(self):
        Ticket.objects.create(
            row=2,
            seat=3,
            flight=self.flight1,
            order=Order.objects.create(user=self.user),
        )
        data = {
            "tickets": [
                {"row": 2, "seat": 3, "flight": self.flight1.id}
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_error_out_of_range(self):
        data = {
            "tickets": [
                {"row": 100, "seat": 3, "flight": self.flight1.id},
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unique_tickets(self):
        data = {
            "tickets": [
                {"row": 2, "seat": 3, "flight": self.flight1.id},
                {"row": 2, "seat": 3, "flight": self.flight1.id}
            ]
        }
        res = self.client.post(ORDER_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "non_field_errors" in res.data or "__all__" in res.data)

    def test_get_authenticated_user(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class OrderUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
