from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Parcel
from .serializers import ParcelSerializer
from apps.tracking.serializers import TrackingEventSerializer

class ParcelCreateView(generics.CreateAPIView):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer

class ParcelListView(generics.ListAPIView):
    serializer_class = ParcelSerializer

    def get_queryset(self):
        return Parcel.objects.filter(sender=self.request.user)

#Tracking public
class ParcelTrackingView(APIView):
    def get(self, request, code):
        try:
            parcel = Parcel.objects.get(tracking_code=code)
        except Parcel.DoesNotExist:
            return Response({"error": "Parcel not found"}, status=404)

        events = parcel.events.all().order_by("created_at")
        serializer = TrackingEventSerializer(events, many=True)

        return Response({
            "tracking_code": parcel.tracking_code,
            "status": parcel.status,
            "events": serializer.data
        })
