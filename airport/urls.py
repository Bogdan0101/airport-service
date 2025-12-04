from django.urls import path, include
from rest_framework import routers
from airport.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("crew", CrewViewSet, basename="crew")
router.register("airports", AirportViewSet, basename="airports")
router.register("routes", RouteViewSet, basename="routes")
router.register("airplane_types",
                AirplaneTypeViewSet,
                basename="airplane_types")
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("flights", FlightViewSet, basename="flights")
router.register("orders", OrderViewSet, basename="orders")
urlpatterns = [path("", include(router.urls))]

app_name = "airport"
