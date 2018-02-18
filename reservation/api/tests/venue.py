import json
from rest_framework import status

from django.test import TestCase, Client
from django.urls import reverse

from core.models import Venue
from core.serializers import VenueSerializer

client = Client()


class VenueTest(TestCase):
    """ Test module for Venue """
    data = [
        ('Hotel Galaxy', 'Outerspace Ln', 'LA', '10000', 'USA'),
        ('Hotel Wonder Place', 'Mystery Island', 'LA', 'WMI 001', 'USA'),
        ('Hotel Black Thunder', 'Bat way', 'Gotham City', '20000', 'USA'),
        ('Hotel Avengers', 'Avengers HQ', 'LA', '90000', 'USA'),
    ]

    def setUp(self):
        timezone = 'America/Los_Angeles'
        fields = ('name', 'address', 'city', 'zipcode', 'country', 'timezone')
        for record in self.data:
            args = dict(zip(fields, record + (timezone,)))
            Venue.objects.create(**args)

    def test_list(self):
        response = client.get(reverse('api:venues'))
        Venues = Venue.objects.all()
        serializer = VenueSerializer(Venues, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get(self):
        random_venue = Venue.objects.order_by('?').first()
        pk = random_venue.pk
        response = client.get(reverse('api:venue', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = VenueSerializer(random_venue)
        self.assertEqual(response.data, serializer.data)

    def test_post_not_allowed(self):
        record = {'name': 'Joker Inn', 'address': 'Joker Ct',
                  'city': 'Gotham City', 'zipcode': 2000, 'country': 'USA',
                  'timezone': 'America/Los_Angeles'}
        response = client.post(reverse('api:venues'), data=record)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_not_allowed(self):
        record = {'name': 'Joker Inn', 'address': 'Joker Ct',
                  'city': 'Gotham City', 'zipcode': 2000, 'country': 'USA',
                  'timezone': 'America/Los_Angeles'}
        response = client.patch(reverse('api:venues'), data=record)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_not_allowed(self):
        record = {'name': 'Joker Inn', 'address': 'Joker Ct',
                  'city': 'Gotham City', 'zipcode': 2000, 'country': 'USA',
                  'timezone': 'America/Los_Angeles'}
        response = client.put(reverse('api:venues'), data=record)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_not_allowed(self):
        random_Venue = Venue.objects.order_by('?').first()
        pk = random_Venue.pk
        response = client.delete(reverse('api:venue', args=[pk]))
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bad_request(self):
        record = {'name': '', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        response = client.post(reverse('api:venues'), data=record)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
