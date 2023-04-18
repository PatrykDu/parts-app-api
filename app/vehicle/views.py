"""
Views for the vehicle API.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Vehicle
from vehicle import serializers


class VehicleViewSet(viewsets.ModelViewSet):
    """View set for manage vehicle APIs"""
    serializer_class = serializers.VehicleDetailSerializer
    queryset = Vehicle.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieves vehicles for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Retrieves the vehicle class for request."""
        if self.action == 'list':
            return serializers.VehicleSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new vehicle."""
        serializer.save(user=self.request.user)
