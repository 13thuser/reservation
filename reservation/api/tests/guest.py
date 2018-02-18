import json
from rest_framework import status

from django.test import TestCase, Client
from django.urls import reverse

from core.models import Guest
from core.serializers import GuestSerializer

client = Client()


class GuestTest(TestCase):
    """ Test module for Guest """
    data = [
        ('Superman', 'Outerspace Ln', 'LA', '10000', 'USA'),
        ('Wonder Woman', 'Mystery Island', 'LA', 'WMI 001', 'USA'),
        ('Batman', 'Bat way', 'Gotham City', '20000', 'USA'),
        ('Thor', 'Galaxy Way', 'LA', '90000', 'USA'),
        ('Hulk', 'Hulk Avenue', 'LA', '90000', 'USA'),
        ('Iron Man', 'Avengers HQ', 'LA', '90000', 'USA'),
    ]

    def setUp(self):
        fields = ('name', 'address', 'city', 'zipcode', 'country')
        for record in self.data:
            args = dict(zip(fields, record))
            Guest.objects.create(**args)

    def test_list(self):
        response = client.get(reverse('api:guests'))
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get(self):
        random_guest = Guest.objects.order_by('?').first()
        pk = random_guest.pk
        response = client.get(reverse('api:guest', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = GuestSerializer(random_guest)
        self.assertEqual(response.data, serializer.data)

    def test_post(self):
        record = {'name': 'Joker', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        response = client.post(reverse('api:guests'), data=record)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pk = response.data['id']
        guest = Guest.objects.get(pk=pk)
        serializer = GuestSerializer(guest)
        self.assertEqual(response.data, serializer.data)

    def test_patch(self):
        record = {'name': 'Joker', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        post_response = client.post(reverse('api:guests'), data=record)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        pk = post_response.data['id']
        patch_record = {'zipcode': 20001}
        response = client.patch(reverse('api:guest', args=[pk]),
                                content_type='application/json',
                                data=json.dumps(patch_record))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        guest = Guest.objects.get(pk=pk)
        self.assertEqual(guest.zipcode, '20001')

    def test_put(self):
        record = {'name': 'Joker', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        post_response = client.post(reverse('api:guests'), data=record)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        pk = post_response.data['id']
        record.update({'zipcode': 20001})
        response = client.put(reverse('api:guest', args=[pk]),
                              content_type='application/json',
                              data=json.dumps(record))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        guest = Guest.objects.get(pk=pk)
        self.assertEqual(guest.zipcode, '20001')

    def test_delete(self):
        random_guest = Guest.objects.order_by('?').first()
        pk = random_guest.pk
        response = client.delete(reverse('api:guest', args=[pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Guest.objects.filter(pk=pk).exists())

    def test_bad_request(self):
        record = {'name': '', 'address': 'Joker Ct', 'city': 'Gotham City',
                  'zipcode': 2000, 'country': 'USA'}
        response = client.post(reverse('api:guests'), data=record)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
