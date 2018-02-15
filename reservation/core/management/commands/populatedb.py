from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from core.models import Venue, Guest, Reservation, Room, Calendar


class Command(BaseCommand):
    help = 'Populates the DB'

    def add_arguments(self, parser):
        pass  # Don't need any arguments

    def _create_user(self, username, email, password):
        user, created = User.objects.get_or_create(username=username,
                                                   defaults={'email': email})
        if created:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
        else:
            print('User %s already exists' % username)

    def handle(self, *args, **options):
        today = date.today()
        print('Creating user test with password test')
        self._create_user('test', 'test@example.com', 'test')
        # Create a hotel
        hotel = Venue(name='HotelABC', address='1 Lane', city='Los Angeles',
                      zipcode='90000')
        hotel.save()
        print('Created Hotel: %s' % hotel)
        # Create Rooms
        room1 = Room(venue=hotel, room_number='1')
        room1.save()
        print('Created Room: %s' % room1)
        room2 = Room(venue=hotel, room_number='2')
        room2.save()
        print('Created Room: %s' % room2)
        room3 = Room(venue=hotel, room_number='3')
        room3.save()
        print('Created Room: %s' % room3)
        # Create Guests
        guest1 = Guest(name='Guest 1', address='ABC', city='Los Angeles',
                       zipcode='90000')
        guest1.save()
        print('Created Guest: %s' % guest1)
        guest2 = Guest(name='Guest 2', address='BOS', city='Boston',
                       zipcode='40000')
        guest2.save()
        print('Created Guest: %s' % guest2)
        # Create a Reservation
        # Guest 1 for 3 days starting today
        three_days = timedelta(days=3)
        reservation1 = Reservation(venue=hotel, room=room1, guest=guest1,
                                   amount=300, checkin=today,
                                   checkout=today + three_days)
        reservation1.save()
        print('Created Reservation #1: %s' % reservation1)
        # Guest 2 for 5 days starting today
        checkin = today + timedelta(days=2)
        five_days = timedelta(days=5)
        reservation2 = Reservation(venue=hotel, room=room2, guest=guest2,
                                   amount=500, checkin=today,
                                   checkout=today + five_days)
        reservation2.save()
        print('Created Reservation #2: %s' % reservation2)
        # Save the reservation in Calendar for future in 30 days
        self._create_calendar(today, today + timedelta(days=30))

    def _create_calendar(self, start, end):
        # Not a very good way of creating calendar, won't scale but ok for this
        # exercise
        day = start
        reservations_map = dict()
        for r in Reservation.objects.all():
            day = r.checkin
            while day < r.checkout:
                day_str = day.strftime('%m/%d/%y')
                reservations_map[(r.venue.id, r.room.id, day_str)] = r
                day += timedelta(days=1)
        records = []
        price = 100  # Assumed Fixed
        print('Creating calendar for next 30 days.')
        day = start
        while day <= end:
            day_str = day.strftime('%m/%d/%y')
            for room in Room.objects.all():
                reservation = reservations_map.get((room.venue.id, room.id,
                                                    day_str))
                if reservation is None:
                    print('%s - %s is available on %s' % (room.venue, room,
                                                          day_str))
                else:
                    print('%s - %s is booked %s' % (room.venue, room,
                                                          day_str))
                records.append(
                    Calendar(room=room, venue=room.venue,
                             day=day, price=price, reservation=reservation)
                )
            day += timedelta(days=1)
        Calendar.objects.bulk_create(records)
