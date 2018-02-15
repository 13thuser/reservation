from django.urls import path, re_path
from . import views

# Api endpoints
# NOTE: for the sake of brevity, venue has been skipped.
# Hence, It is assumed that there'll be only a single venue.
urlpatterns = [
    path('guests', views.GuestList.as_view()),
    path('guests/<int:pk>', views.GuestDetail.as_view()),
    path('reservations', views.ReservationList.as_view()),
    path('reservations/<int:pk>', views.ReservationDetail.as_view()),
    path('rooms', views.RoomList.as_view()),
    path('rooms/<int:pk>', views.RoomDetail.as_view()),
    # Venues create update delete via api is prohibited
    path('venues/<int:pk>', views.VenueDetail.as_view()),
    path('calendar', views.CalendarList.as_view()),
    re_path(r'calendar/(?P<date>\d{4}-\d{2}-\d{2})',
            views.CalendarDayList.as_view()),
]
