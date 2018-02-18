from django.db.models import Q
from rest_framework import serializers
from .models import Venue, Guest, Reservation, Room, Calendar

# NOTE: for the brevity of this exercise it's assumed that there
# will one venue/hotel, so venue api is not covered:


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ('id', 'name', 'address', 'city', 'zipcode', 'country')
        read_only_fields = ('id',)


class RoomSerializer(serializers.ModelSerializer):
    venue_id = serializers.IntegerField(source='venue.id')

    class Meta:
        model = Room
        fields = ('id', 'venue_id', 'room_number', 'room_type', 'room_desc')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        venue = validated_data.pop('venue', None)
        if venue is not None:
            instance.venue_id = venue['id']
        return super(RoomSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        venue_id = validated_data.pop('venue')['id']
        venue = Venue.objects.get(pk=venue_id)
        return Room.objects.create(venue=venue, **validated_data)


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ('id', 'name', 'address', 'city', 'zipcode', 'country')
        read_only_fields = ('id',)


class ReservationSerializer(serializers.ModelSerializer):
    venue_id = serializers.IntegerField(source='venue.id')
    guest_id = serializers.IntegerField(source='guest.id')
    room_id = serializers.CharField(source='room.id')

    class Meta:
        model = Reservation
        fields = ('id', 'amount', 'state', 'checkin', 'checkout',
                  'venue_id', 'guest_id', 'room_id',)
        read_only_fields = ('id', 'created_at', 'updated_at',
                            'venue', 'guest', 'room')

    def update(self, instance, validated_data):
        guest = validated_data.pop('guest', None)
        if guest:
            instance.guest_id = guest['id']
        venue = validated_data.pop('venue', None)
        if venue:
            instance.venue_id = venue['id']
        room = validated_data.pop('room', None)
        if room:
            instance.room_id = room['id']
        return super(ReservationSerializer, self) \
            .update(instance, validated_data)

    def create(self, validated_data):
        dct_guest = validated_data.pop('guest')
        dct_venue = validated_data.pop('venue')
        dct_room = validated_data.pop('room')
        venue = Venue.objects.get(pk=dct_venue['id'])
        guest = Guest.objects.get(pk=dct_guest['id'])
        room = Room.objects.get(venue=venue, pk=dct_room['id'])
        return Reservation.objects.create(venue=venue, guest=guest, room=room,
                                          **validated_data)


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ('id', 'room_id', 'venue_id', 'day', 'price', 'reservation_id')
        read_only_fields = ('id',)
