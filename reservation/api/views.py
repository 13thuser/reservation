from datetime import datetime as dt
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from core.models import Guest, Reservation, Room, Calendar, Venue
from core.serializers import (GuestSerializer, ReservationSerializer,
                              RoomSerializer, CalendarSerializer,
                              VenueSerializer)

from functools import wraps


class GuestList(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class RoomList(generics.ListCreateAPIView):
    serializer_class = RoomSerializer

    # Allows you to search:
    #   /api/rooms
    #   /api/rooms?venue_id=1
    #   /api/rooms?room_number=3
    #   /api/rooms?venue_id=1&room_number=3
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


class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class RoomDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# Only allow venue retrieval by id
class VenueDetail(generics.RetrieveAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


# ********************************************************
# Calendar/Booking needs custom end-points
# Only list and detail endpoints are allowed
# Delete and update are suppose to be done by back-end job
# ********************************************************
class CalendarList(generics.ListCreateAPIView):
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
