"""
Serializers for the vehicle API view.
"""
from rest_framework import serializers

from core.models import (
    Vehicle,
    Tag,
    )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for vehicles."""
    tags = TagSerializer(many=True, required=False) # many means it will be a list of tags

    class Meta:
        model = Vehicle
        fields = ['id', 'title', 'year', 'price', 'link', 'tags']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Create a vehicle."""
        tags = validated_data.pop('tags', [])
        vehicle = Vehicle.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            vehicle.tags.add(tag_obj)

        return vehicle

class VehicleDetailSerializer(VehicleSerializer):
    """Serializer for vehicle detail view"""

    class Meta(VehicleSerializer.Meta):
        fields = VehicleSerializer.Meta.fields + ['description']

