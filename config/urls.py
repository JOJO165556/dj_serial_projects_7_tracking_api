from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    path('api/users/', include("apps.users.urls")),
    path('api/parcels/', include("apps.parcels.urls")),
    path('api/couriers/', include("apps.couriers.urls")),
    path('api/dashboard/', include("apps.dashboard.urls")),
    path('api/analytics/', include("apps.analytics.urls")),
    path('api/notifications/', include("apps.notifications.urls")),
]

urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
    path('api/redoc/', SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
