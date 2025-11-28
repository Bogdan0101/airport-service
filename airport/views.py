from datetime import datetime

from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from airport.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneTypeRetrieveSerializer,
    FlightSerializer,
    FlightRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
)
from airport.models import (
    Crew,
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Flight,
    Order,
    Ticket,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        last_name = self.request.GET.get("last_name")
        first_name = self.request.GET.get("first_name")
        queryset = self.queryset
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        return queryset.distinct()


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        source = self.request.GET.get("source")
        destination = self.request.GET.get("destination")
        queryset = self.queryset
        if source:
            queryset = queryset.filter(source__name__icontains=source)
        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)
        return queryset.distinct()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer
        return AirplaneTypeSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (Flight.objects
                .select_related("route", "route__source", "route__destination", "airplane", )
                .prefetch_related("crew")
                )
    serializer_class = FlightSerializer

    def get_queryset(self):
        departure_time = self.request.GET.get("departure_time")
        arrival_time = self.request.GET.get("arrival_time")
        queryset = self.queryset
        if departure_time:
            departure_time = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_time)
        if arrival_time:
            arrival_time = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_time)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
