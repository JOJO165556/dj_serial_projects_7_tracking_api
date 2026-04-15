from django.urls import path
from .views import CourierUpdateLocationView, AvailableCouriersView

urlpatterns = [
    path('me/', CourierUpdateLocationView.as_view()),
    path("available/", AvailableCouriersView.as_view()),
]
