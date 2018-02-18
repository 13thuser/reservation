import json
from datetime import date, timedelta
from rest_framework import status

from django.test import TestCase, Client
from django.urls import reverse

from core.models import Calendar, Room, Venue, Reservation, Guest
from core.serializers import CalendarSerializer

from .guest import GuestTest

client = Client()


class CalendarTest(TestCase):
    """ Test module for Calendar """
    venue_values = ('Hotel Galaxy', 'Outerspace Ln', 'LA', '10000', 'USA',
                    'America/Los_Angeles'),
    venue_fields = ('name', 'address', 'city', 'zipcode', 'country', 'timezone')
    venue_args = dict(zip(venue_fields, venue_values))

    room_fields = ('room_number', 'room_type', 'room_desc')
    room_values = ('1A', 'Regular', 'Regular Small Calendar')
    room_args = dict(zip(room_fields, room_values))

    guest_fields = ('name', 'address', 'city', 'zipcode', 'country')
    guest_values = ('Superman', 'Outerspace Ln', 'LA', '10000', 'USA'),
    guest_args = dict(zip(guest_fields, guest_values))

    today = date.today()
    five_days = today + timedelta(days=5)
    reservation_fields = ('amount', 'state', 'checkin', 'checkout')
    reservation_values = (500, Reservation.FUTURE, today, five_days)
    reservation_args = dict(zip(reservation_fields, reservation_values))

    def setUp(self):
        venue = Venue.objects.create(**self.venue_args)
        room_args = {'venue': venue}
        room_args.update(self.room_args)
        room = Room.objects.create(**room_args)
        guest = Guest.objects.create(**self.guest_args)
        reservation_args = {'venue': venue, 'room': room, 'guest': guest}
        reservation_args.update(**self.reservation_args)
        reservation = Reservation.objects.create(**reservation_args)

        period = reservation.checkout - reservation.checkin
        price = reservation.amount / period.days
        day = reservation.checkin
        while day < reservation.checkout:
            Calendar.objects.create(**{'room': room, 'venue': venue,
                                       'day': day, 'price': price})
            day += timedelta(days=1)

    def test_list(self):
        response = client.get(reverse('api:calendar'))
        calendar = Calendar.objects.all()
        serializer = CalendarSerializer(calendar, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_date(self):
        today = date.today()
        date_fmt = today.strftime('%Y-%m-%d')
        response = client.get(reverse('api:calendar_day', args=[date_fmt]))
        calendar = Calendar.objects.filter(day=today)
        serializer = CalendarSerializer(calendar, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
