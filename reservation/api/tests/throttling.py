import json
from datetime import date, timedelta
from random import randint

from rest_framework import status
from rest_framework.test import APITestCase

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from core.models import Room, Venue, Reservation, Guest
from core.serializers import ReservationSerializer

client = Client()


class ThrottlingTest(APITestCase):
    """ Test module for Reservation """
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

    def setUp(self):
        venue = Venue.objects.create(**self.venue_args)
        room_args = {'venue': venue}
        room_args.update(self.room_args)
        room = Room.objects.create(**room_args)
        guest = Guest.objects.create(**self.guest_args)

    def tearDown(self):
        # HACK: clear the cache because we cannot override the throttling
        # settings
        from django.core.cache import caches
        api_cache = caches._caches.caches['api']
        api_cache.clear()

    def _create_reservation_dict(self, checkin, checkout):
        venue = Venue.objects.order_by('?').first()
        room = Room.objects.order_by('?').first()
        guest = Guest.objects.order_by('?').first()
        record = {'venue_id': venue.id, 'room_id': room.id,
                  'guest_id': guest.id, 'amount': 100, 'state': 0,
                  'checkin': checkin.strftime('%Y-%m-%d'),
                  'checkout': checkout.strftime('%Y-%m-%d')}
        return record

    def test_throttle(self):
        today = date.today()
        checkin = today + timedelta(days=10)
        checkout = today + timedelta(days=11)
        record = self._create_reservation_dict(checkin, checkout)
        post_response = client.post(reverse('api:reservations'), data=record)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        pk = post_response.data['id']
        patch_record = {'state': 1}
        response = client.patch(reverse('api:reservation', args=[pk]),
                                content_type='application/json',
                                data=json.dumps(patch_record))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = client.patch(reverse('api:reservation', args=[pk]),
                                content_type='application/json',
                                data=json.dumps(patch_record))
        self.assertEqual(response.status_code,
                         status.HTTP_429_TOO_MANY_REQUESTS)
        put_record = record
        response = client.put(reverse('api:reservation', args=[pk]),
                              content_type='application/json',
                              data=json.dumps(put_record))
        self.assertEqual(response.status_code,
                         status.HTTP_429_TOO_MANY_REQUESTS)
