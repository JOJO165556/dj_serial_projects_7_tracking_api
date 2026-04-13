from django.urls import path
from .views import ParcelCreateView, ParcelListView, ParcelTrackingView, AssignCourierView

urlpatterns = [
    path("", ParcelListView.as_view(), name="parcels"),
    path("create/", ParcelCreateView.as_view(), name="create"),
    path("track/<str:code>/", ParcelTrackingView.as_view(), name="track"),
    path("assign/<uuid:parcel_id>/", AssignCourierView.as_view()),
]