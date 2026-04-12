from rest_framework import generics
from .models import CourierProfile
from .serializers import CourierSerializer

class CourierUpdateLocationView(generics.UpdateAPIView):
    serializer_class = CourierSerializer

    def get_object(self):
        return CourierProfile.objects.get(user=self.request.user)

class AvailableCouriersView(generics.ListAPIView):
    serializer_class = CourierSerializer

    def get_queryset(self):
        return CourierProfile.objects.filter(is_available=True)