"""
Serializers for the vehicle API view.
"""
from rest_framework import serializers

from core.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Vehicle
        fields = ['id', 'title', 'year', 'price', 'link']
        read_only_fields = ['id']
