from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('', include('core.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]
