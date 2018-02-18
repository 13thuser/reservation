import json
from datetime import date, timedelta
from random import randint

from rest_framework import status

from django.test import TestCase, Client
from django.urls import reverse

from core.models import Room, Venue, Reservation, Guest
from core.serializers import ReservationSerializer

client = Client()


class ReservationTest(TestCase):
    """ Test module for Reservation """
    venue_values = ('Hotel Galaxy', 'Outerspace Ln', 'LA', '10000', 'USA',
                    'America/Los_Angeles'),
    venue_fields = ('name', 'address', 'city', 'zipcode', 'country', 'timezone')
    venue_args = dict(zip(venue_fields, venue_values))

    room_fields = ('room_number', 'room_type', 'room_desc')
    room_values = ('1A', 'Regular', 'Regular Small Calendar')
    room_args = dict(zip(room_fields, room_values))

    guest_fields = ('name', 'address', 'city', 'zipcode', 'country')
    guest1_values = ('Superman', 'Outerspace Ln', 'LA', '10000', 'USA'),
    guest2_values = ('Wonder Woman', 'Mystery Island', 'LA', 'WMI 001', 'USA'),
    guest1_args = dict(zip(guest_fields, guest1_values))
    guest2_args = dict(zip(guest_fields, guest2_values))

    def setUp(self):
        venue = Venue.objects.create(**self.venue_args)
        room_args = {'venue': venue}
        room_args.update(self.room_args)
        room = Room.objects.create(**room_args)
        guest1 = Guest.objects.create(**self.guest1_args)
        guest2 = Guest.objects.create(**self.guest2_args)

        today = date.today()

        checkin1 = today + timedelta(days=1)
        checkout1 = today + timedelta(days=5)
        Reservation.objects.create(**{'venue': venue, 'room': room,
                                      'guest': guest1, 'amount': 100,
                                      'state': 0, 'checkin': checkin1,
                                      'checkout': checkout1})

        checkin2 = today + timedelta(days=6)
        checkout2 = today + timedelta(days=8)
        Reservation.objects.create(**{'venue': venue, 'room': room,
                                      'guest': guest2, 'amount': 100,
                                      'state': 0, 'checkin': checkin2,
                                      'checkout': checkout2})

    def test_list(self):
        response = client.get(reverse('api:reservations'))
        Reservations = Reservation.objects.all()
        serializer = ReservationSerializer(Reservations, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get(self):
        random_Reservation = Reservation.objects.order_by('?').first()
        pk = random_Reservation.pk
        response = client.get(reverse('api:reservation', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReservationSerializer(random_Reservation)
        self.assertEqual(response.data, serializer.data)

    def _create_reservation_dict(self, checkin, checkout):
        venue = Venue.objects.order_by('?').first()
        room = Room.objects.order_by('?').first()
        guest = Guest.objects.order_by('?').first()
        record = {'venue_id': venue.id, 'room_id': room.id,
                  'guest_id': guest.id, 'amount': 100, 'state': 0,
                  'checkin': checkin, 'checkout': checkout}
        return record

    def test_post(self):
        today = date.today()
        checkin = today + timedelta(days=10)
        checkout = today + timedelta(days=11)
        record = self._create_reservation_dict(checkin, checkout)
        response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.data['id']
        reservation = Reservation.objects.get(pk=pk)
        serializer = ReservationSerializer(reservation)
        self.assertEqual(response.data, serializer.data)

    def test_post_booking_validation(self):
        """ The specific room should not be previously booked """
        today = date.today()
        checkin = today + timedelta(days=0)
        checkout = today + timedelta(days=2)
        record = self._create_reservation_dict(checkin, checkout)
        response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        checkin = today + timedelta(days=5)
        checkout = today + timedelta(days=7)
        record = self._create_reservation_dict(checkin, checkout)
        response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_before_checkin(self):
        """ Checkout cannot be before checkin """
        today = date.today()
        checkin = today + timedelta(days=15)
        checkout = today + timedelta(days=12)
        record = self._create_reservation_dict(checkin, checkout)
        response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        random_Reservation = Reservation.objects.order_by('?').first()
        pk = random_Reservation.pk
        response = client.delete(reverse('api:reservation', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(pk=pk).exists())

    def test_bad_request(self):
        record = {'name': '', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
