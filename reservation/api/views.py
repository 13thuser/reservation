from datetime import datetime as dt
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.exceptions import ValidationError

from core.models import Guest, Reservation, Room, Calendar, Venue
from core.serializers import (GuestSerializer, ReservationSerializer,
                              RoomSerializer, CalendarSerializer,
                              VenueSerializer)

from .throttling import MethodBasedThrottlingMixin
from .exception_handler import api_exception_handler


# Guest API
class GuestList(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


# Room API
class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class RoomList(generics.ListCreateAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        queryset = Room.objects.all()
        query_params = self.request.query_params
        venue_id = query_params.get('venue_id', None)
        room_number = query_params.get('room_number', None)
        if venue_id or room_number:
            query = {}
            if venue_id:
                query['venue__id'] = venue_id
            if room_number:
                query['room_number'] = room_number
            queryset = queryset.filter(**query)
        return queryset


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


# Update methods are throttled to 1 call/minute only if updated in last 1 min.
# state_change is configurable in settings.py
class ReservationDetail(MethodBasedThrottlingMixin,
                        generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    throttle_scope = 'state_change'
    THROTTLED_METHODS = set(['put', 'patch'])
    resource_id_field = 'pk'

    # Put 'put' and 'patch' into one group
    def get_method_group_id(self, method):
        if method in ['put', 'patch']:
            return 'update'
        return method


# Only allow venue retrieval by id and list
# Because adding a venue can have such an huge business impact, so we're not
# allowing unsafe methods via api
class VenueList(generics.ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class VenueDetail(generics.RetrieveAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


# ********************************************************
# Calendar/Booking needs custom end-points
# Only list and detail endpoints are allowed
# Delete and update are suppose to be done by back-end job
# ********************************************************
class CalendarList(generics.ListAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer


class CalendarDayList(generics.ListAPIView):
    serializer_class = CalendarSerializer

    def get_queryset(self):
        data = self.kwargs['date']
        day = dt.strptime(data, '%Y-%m-%d').date()
        return Calendar.objects.filter(day=day)


class CalendarDetail(generics.RetrieveAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
