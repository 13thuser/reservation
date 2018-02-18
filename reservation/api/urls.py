from django.urls import path, re_path
from . import views

# Api endpoints
urlpatterns = [
    path('guests', views.GuestList.as_view(), name='guests'),
    path('guest/<int:pk>', views.GuestDetail.as_view(), name='guest'),
    path('reservations', views.ReservationList.as_view(), name='reservations'),
    path('reservation/<int:pk>', views.ReservationDetail.as_view(),
         name='reservation'),
    path('rooms', views.RoomList.as_view(), name='rooms'),
    path('room/<int:pk>', views.RoomDetail.as_view(), name='room'),
    # Venues methods create update delete via api is prohibited
    path('venues', views.VenueList.as_view(), name='venues'),
    path('venue/<int:pk>', views.VenueDetail.as_view(), name='venue'),
    path('calendar', views.CalendarList.as_view(), name='calendar'),
    re_path(r'calendar/(?P<date>\d{4}-\d{2}-\d{2})',
            views.CalendarDayList.as_view(), name='calendar_day'),
]
