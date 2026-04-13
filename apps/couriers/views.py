from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import CourierProfile
from .serializers import CourierSerializer
from .utils import calculate_distance


class CourierUpdateLocationView(generics.UpdateAPIView):
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        if user.role != "courier":
            raise PermissionDenied("Only couriers can update location")
        try:
            return CourierProfile.objects.get(user=user)
        except CourierProfile.DoesNotExist:
            raise NotFound("Courier profile not found")

#Trouver les livreurs disponibles
class AvailableCouriersView(APIView):
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        try:
            lat = float(lat) if lat else None
            lng = float(lng) if lng else None
        except ValueError:
            return Response({"error": "Invalid coordinates"}, status=400)

        couriers = CourierProfile.objects.filter(is_available=True)
        result = []
        for c in couriers:
            if c.latitude is None or c.longitude is None:
                continue

            distance = None

            if lat is not None and lng is not None:
                distance = calculate_distance(
                    lat,
                    lng,
                    c.latitude,
                    c.longitude
                )

            result.append({
                "id": c.id,
                "user": c.user.username,
                "lat": c.latitude,
                "lng": c.longitude,
                "distance": distance
            })

        #Tri si distance existe
        if lat is not None and lng is not None:
            result.sort(key=lambda x: x["distance"] if x["distance"] is not None else 9999)

        return Response(result)