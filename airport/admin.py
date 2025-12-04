from django.contrib import admin
from airport.models import (Airport,
                            Crew,
                            Route,
                            Flight,
                            Airplane,
                            AirplaneType,
                            Ticket,
                            Order)

admin.site.register(Airport)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(AirplaneType)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(Airplane)
