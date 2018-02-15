from django.contrib import admin
from .models import Venue, Guest, Reservation, Room, Calendar

admin.site.register(Venue)
admin.site.register(Guest)
admin.site.register(Reservation)
admin.site.register(Room)
admin.site.register(Calendar)
