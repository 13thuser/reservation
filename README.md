# Reservation
A sample coding project.

Developed using python version `3.6.4` and Django version `2.0.2`.

##Summary

This project implements rest api for hypothetical venues and the reservation workflow.

It supports following features:

- **API Endpoints**: Rest APIs for almost all of the entities. A very few are restricted or prohibited considering business impact.
- **Browseable API**: All of the endpoints are browsable via any modern browser.
- **Tests**: Tests are available for all of the entities and their supported methods. See [Tests](#Tests) section about how to run tests.
- **Throttling**: State change methods (PUT, PATCH) are throttled to `1/minute` per resource. The throttled endpoint is `/api/reservations/:id`


##Setup


	1. Clone this repository
	2. cd <repository folder>
	3. pip install -r requirements.txt
	4. cd reservation
	5. python manage.py makemigrations
	6. python manage.py migrate

## Initial Data	

You can execute the following command to generate some sample data to play with or browse:

	python manage.py command
	

## Browseable APIs

To browse APIs using browser, run the dev webserver:

	python manage.py runserver
	
By default, it will run on port `8000`, and you can hit an example url `http://localhost:8000/api/guests` to see list of options supported by the api endpoints. API enpoints are listed in [Api Endpoints](#api-endpoints) section below.


## Tests
 
 Run tests with the following command:
 
	python manage.py test


## API Enpoints

The example enpoints are listed below. They are browsable as well.

	# Guests API
	http://localhost:8000/api/guests
	[GET, POST, HEAD, OPTIONS]
	
	http://localhost:8000/api/guest/<:id>
	[GET, PUT, PATCH, DELETE, HEAD, OPTIONS]
	
	# Venue API
	http://localhost:8000/api/venues
	[GET, HEAD, OPTIONS]
	
	http://localhost:8000/api/venues/<:id>
	[GET, HEAD, OPTIONS]
	
	# Rooms API
	http://localhost:8000/api/rooms
	[GET, POST, HEAD, OPTIONS]
	
	http://localhost:8000/api/room/<:id>
	GET, PUT, PATCH, DELETE, HEAD, OPTIONS
	
	# Reservation
	http://localhost:8000/api/reservations
	[GET, POST, HEAD, OPTIONS]
	
	# PUT and PATCH are throttled 1 call/minute per <:id>
	http://localhost:8000/api/reservations/<:id>
	[GET, PUT, PATCH, DELETE, HEAD, OPTIONS]
	
	# Calendar
	http://localhost:8000/api/calendar
	[GET, HEAD, OPTIONS]
	
	http://localhost:8000/api/calendar/<:yyyy-mm-dd>
	[GET, HEAD, OPTIONS]
