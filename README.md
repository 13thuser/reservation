Setup:

In repository folder, execute the following commands:

1. pip install -r requirements.txt

2. cd reservation

3. python manage.py migrate

4. python manage.py populatedb
   (Implemented as django manage command)

5. python manage.py runsever

6. Open http://localhost:8000/api/... (see api endpoints below)

SUMMARY:

Tried to implement various different features in a short time
 (few hours/days for 2 days)

Implemented:


/api/venues/<id>
    GET - Gives you venue details. Due to shortage of time, no listing
          endpoint is done.
    DELETE is not allowed

/api/guests
    GET - Gives you a list of guests
    POST - Creates a new guest    
    DELETE - Deletes a Guest

/api/rooms

    GET - list of rooms
    GET - Allows you to search:
      /api/rooms?venue_id=1
      /api/rooms?room_number=3
      /api/rooms?venue_id=1&room_number=3

    POST - json data to create new room.
           Error will tell you what fields are required

/api/reservations

    GET - returns a list of reservations
    POST - creates a new reservation 

The Calendar table will be populated behind the scenes by a backend job,
 so the creating objects in the calendar are not allowed.

/api/calendar

    GET - returns a list of bookings, 10 items per page

/api/calendar/<yyyy-mm-dd>

    GET - returns a list of bookings for that date, 10 items per page

Default pagination: 10 items / page


WHAT's NOT DONE

- Tests: Sorry, ran out of time. For your convenience to look at api end points
please use tool like Postman.
- Dockerization: Again, due to timing constraints, it was not implemented.
- Misc endpoints
- Some assumptions were made, since this was a take-home exercise.
