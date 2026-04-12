from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include("apps.users.urls")),
    path('api/parcels/', include("apps.parcels.urls")),
    path('api/couriers/', include("apps.couriers.urls")),
]
