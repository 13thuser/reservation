from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('', include('core.urls')),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('admin/', admin.site.urls),
]
