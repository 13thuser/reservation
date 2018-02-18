from django.db.models import Q
from django.db import models

from rest_framework.exceptions import ValidationError


class AddressMixin(models.Model):
    # Abstract class for the address
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='United States')

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        unique_together = (('name', 'address', 'city', 'country'),)
        ordering = ['id']


class Venue(AddressMixin):
    # Venue can be any  - hotel / hospital / etc
    #
    # name, address, city, zipcode and country comes from AddressMixin
    #
    # Timezone is very helpful to keep up with reservation when the venues are
    # spread accross muliple timezones. The idea here is to save reservation
    # and time related information in UTC or local time (choose one) but can
    # be helpful in various scenarios.
    # For los angeles/PST, the value is 'America/Los_Angeles'
    timezone = models.CharField(max_length=100, blank=False)
    # Enable or disable venues, tells us if venue is operating or can also be
    # used to tell if venue is accepting any reservations.
    disabled = models.BooleanField(default=False)
    #
    # You can add more fields here: check-in time, checkout-time etc

    class Meta:
        ordering = ['id']


class Guest(AddressMixin):
    # Guess Information
    #
    # name, address, city, zipcode and country comes from AddressMixin
    #

    class Meta:
        ordering = ['id']


class Reservation(models.Model):
    FUTURE, CHECK_IN, CHECK_OUT = 0, 1, 2
    # We can also add additional states like No Show
    STATES = list((s, s) for s in (FUTURE, CHECK_IN, CHECK_OUT))

    # Reservation details
    venue = models.ForeignKey('Venue', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    guest = models.ForeignKey('Guest', on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    state = models.IntegerField(choices=STATES, default=FUTURE, db_index=True)
    checkin = models.DateField(db_index=True)
    checkout = models.DateField()
    # Number of adults and kids have been ignored
    # There will be 1 reservation record for 1 room
    # Additional checks to figure out if the given rooms/dates have already
    # booked have been ignored

    def clean(self, *args, **kwargs):
        # Assumption: Guest cannot check-in and check-out on the same day
        # assuming that the guest to book for atleast 1 day.
        if self.checkin >= self.checkout:
            raise ValidationError({'error': 'checkin date should be less than '
                                            'checkout date.'})

        # Assumption: Guest 1 can check-out and Guest 2 can check-in on the
        # same day
        filters = (Q(checkin__lte=self.checkin, checkout__gt=self.checkin) |
                   Q(checkin__lt=self.checkout, checkout__gte=self.checkout))
        if self.pk:
            # If modifying, the don't check for current one
            filters &= ~Q(pk=self.pk)
        if Reservation.objects.filter(
           filters,
           venue__id=self.venue_id, room__id=self.room_id
           ).exists():
            raise ValidationError({'error': 'There is an existing reservation '
                                            'for this Room'})

        return super(Reservation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Reservation, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: %s :: %s' % (self.venue, self.room, self.state)

    class Meta:
        indexes = [models.Index(fields=['guest', 'venue', 'room'])]
        ordering = ['id']


class Room(models.Model):
    # Room Information
    REGULAR = 'Regular'
    ROOM_TYPES = (REGULAR, 'Deluxe', 'Suite')  # Some sample room types
    ROOM_TYPES_CHOICES = list((c, c) for c in ROOM_TYPES)

    venue = models.ForeignKey('Venue', db_index=True, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=100, choices=ROOM_TYPES_CHOICES,
                                 default=REGULAR, db_index=True)
    room_desc = models.TextField(blank=True)
    # You can extend it with additional fields including details
    # about rooms / units

    def __str__(self):
        return 'Room #%s (%s)' % (self.room_number, self.room_type)

    class Meta:
        unique_together = (('venue', 'room_number'),)
        indexes = [models.Index(fields=['venue', 'room_number'])]
        ordering = ['id']


class Calendar(models.Model):
    """ Calendar/Inventory - Store record for every venue and price per day
    This table will be updated by background job with latest price info for
    future dates, It will serve as a calendar to the new guests to check the
    dates available"""
    reservation = models.ForeignKey('Reservation', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    room = models.ForeignKey('Room', db_index=True, on_delete=models.CASCADE)
    venue = models.ForeignKey('Venue', db_index=True, on_delete=models.CASCADE)
    day = models.DateField(db_index=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return '%s - %s: %s' % (self.day, self.venue, self.room)

    class Meta:
        unique_together = (('venue', 'room', 'day'))
        indexes = [models.Index(fields=['venue', 'room', 'day'])]
        ordering = ['id']
