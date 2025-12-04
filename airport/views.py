from datetime import datetime
from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
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
    AirplaneImageSerializer,
    AirplaneRetrieveSerializer,
    AirplaneTypeRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
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
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().order_by("id")
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

    @extend_schema(parameters=[
        OpenApiParameter(
            name="last_name",
            type=str,
            description="Filter by last name(ex. ?last_name=Walker)",
        ),
        OpenApiParameter(
            name="first_name",
            type=str,
            description="Filter by first name (ex. ?first_name=John)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().order_by("id")
    serializer_class = AirportSerializer

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()

    @extend_schema(parameters=[
        OpenApiParameter(
            name="name",
            type=str,
            description="Filter by name (ex. ?name=Boryspil)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = (Route.objects.all()
                .select_related("source", "destination")
                .order_by("id")
                )

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
            queryset = (queryset.
                        filter(source__name__icontains=source))
        if destination:
            queryset = (queryset.
                        filter(destination__name__icontains=destination))
        return queryset.distinct()

    @extend_schema(parameters=[
        OpenApiParameter(
            name="source",
            type=str,
            description="Filter by source (ex. ?source=Boryspil)",
        ),
        OpenApiParameter(
            name="destination",
            type=str,
            description="Filter by destination (ex. ?destination=Chopin)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all().order_by("id")
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

    @extend_schema(parameters=[
        OpenApiParameter(
            name="name",
            type=str,
            description="Filter by name (ex. ?name=Boeing)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().order_by("id")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific movie"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.distinct()

    @extend_schema(parameters=[
        OpenApiParameter(
            name="name",
            type=str,
            description="Filter by name (ex. ?name=SkyBird)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .select_related(
            "route",
            "airplane",
            "route__source",
            "route__destination")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
        .order_by("id")
    )
    serializer_class = FlightSerializer

    def get_queryset(self):
        departure_time = self.request.GET.get("departure_time")
        arrival_time = self.request.GET.get("arrival_time")
        queryset = self.queryset
        if departure_time:
            departure_time = datetime.strptime(
                departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_time)
        if arrival_time:
            arrival_time = datetime.strptime(
                arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arrival_time)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    @extend_schema(parameters=[
        OpenApiParameter(
            name="departure_time",
            type=str,
            description="Filter departure time by date(ex. ?date=2022-01-10)",
        ),
        OpenApiParameter(
            name="arrival_time",
            type=str,
            description="Filter arrival time by date(ex. ?date=2022-01-10)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = (Order.objects.all()
                .select_related("user", )
                .prefetch_related("tickets",
                                  "tickets__flight",
                                  "tickets__flight__route",
                                  )
                .order_by("id")
                )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(parameters=[
        OpenApiParameter(
            name="created_at",
            type=str,
            description="Filter by created date (ex. ?created_at=2022-01-10)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        created_at = self.request.GET.get("created_at")
        queryset = self.queryset.filter(user=self.request.user)
        if created_at:
            created_at = datetime.strptime(created_at, "%Y-%m-%d").date()
            queryset = queryset.filter(created_at__date=created_at)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
