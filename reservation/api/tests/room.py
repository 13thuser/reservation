import json
from rest_framework import status

from django.test import TestCase, Client
from django.urls import reverse

from core.models import Room, Venue
from core.serializers import RoomSerializer

client = Client()


class RoomTest(TestCase):
    """ Test module for Room """
    data = [
        ('1A', 'Regular', 'Regular Small Room'),
        ('1B', 'Regular', 'Regular Small Room'),
        ('101', 'Deluxe', 'Deluxe Room'),
        ('102', 'Deluxe', 'Deluxe Room'),
        ('B007', 'Suite', 'James Bond themed Suite'),
        ('A001', 'Suite', 'Avengers HQ themed Suite'),
    ]
    venue = ('Hotel Galaxy', 'Outerspace Ln', 'LA', '10000', 'USA',
             'America/Los_Angeles'),
    venue_fields = ('name', 'address', 'city', 'zipcode', 'country', 'timezone')
    venue_args = dict(zip(venue_fields, venue))

    def setUp(self):
        venue = Venue.objects.create(**self.venue_args)
        fields = ('venue', 'room_number', 'room_type', 'room_desc')
        for record in self.data:
            args = dict(zip(fields, (venue,) + record))
            Room.objects.create(**args)

    def test_list(self):
        response = client.get(reverse('api:rooms'))
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get(self):
        random_room = Room.objects.order_by('?').first()
        pk = random_room.pk
        response = client.get(reverse('api:room', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = RoomSerializer(random_room)
        self.assertEqual(response.data, serializer.data)

    def test_post(self):
        venue = Venue.objects.order_by('?').first()
        record = {'venue_id': venue.id, 'room_number': 'A002',
                  'room_type': 'Suite',
                  'room_desc': 'Avengers HQ themed Second Suite'}
        response = client.post(reverse('api:rooms'), data=record)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.data['id']
        room = Room.objects.get(pk=pk)
        serializer = RoomSerializer(room)
        self.assertEqual(response.data, serializer.data)

    def test_patch(self):
        venue = Venue.objects.order_by('?').first()
        record = {'venue_id': venue.id, 'room_number': 'A002',
                  'room_type': 'Suite',
                  'room_desc': 'Avengers HQ themed Second Suite'}
        post_response = client.post(reverse('api:rooms'), data=record)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        pk = post_response.data['id']
        patch_record = {'room_type': 'Deluxe'}
        response = client.patch(reverse('api:room', args=[pk]),
                                content_type='application/json',
                                data=json.dumps(patch_record))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room = Room.objects.get(pk=pk)
        self.assertEqual(room.room_type, 'Deluxe')

    def test_put(self):
        venue = Venue.objects.order_by('?').first()
        record = {'venue_id': venue.id, 'room_number': 'A002',
                  'room_type': 'Suite',
                  'room_desc': 'Avengers HQ themed Second Suite'}
        post_response = client.post(reverse('api:rooms'), data=record)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        pk = post_response.data['id']
        record.update({'room_type': 'Deluxe'})
        response = client.put(reverse('api:room', args=[pk]),
                              content_type='application/json',
                              data=json.dumps(record))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        room = Room.objects.get(pk=pk)
        self.assertEqual(room.room_type, 'Deluxe')

    def test_delete(self):
        random_room = Room.objects.order_by('?').first()
        pk = random_room.pk
        response = client.delete(reverse('api:room', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(pk=pk).exists())

    def test_bad_request(self):
        record = {'venue_id': 1, 'room_type': 'Suite',
                  'room_desc': 'Avengers HQ themed Suite'}
        response = client.post(reverse('api:rooms'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
