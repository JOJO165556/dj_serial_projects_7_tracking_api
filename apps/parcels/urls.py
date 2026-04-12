from django.urls import path
from .views import ParcelCreateView, ParcelListView, ParcelTrackingView

urlpatterns = [
    path("", ParcelListView.as_view(), name="parcels"),
    path("create/", ParcelCreateView.as_view(), name="create"),
    path("track/<str:code>/", ParcelTrackingView.as_view(), name="track"),
]