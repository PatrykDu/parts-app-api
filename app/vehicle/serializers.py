"""
Serializers for the vehicle API view.
"""
from rest_framework import serializers

from core.models import (
    Vehicle,
    Tag,
    Part,
    )


class PartSerializer(serializers.ModelSerializer):
    """Serializer for parts."""

    class Meta:
        model = Part
        fields = ['id', 'name', 'price']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for vehicles."""
    # many means it will be a list of tags
    tags = TagSerializer(many=True, required=False)
    parts = PartSerializer(many=True, required=False)

    class Meta:
        model = Vehicle
        fields = ['id', 'title', 'year', 'price', 'link', 'tags', 'parts', ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, vehicle):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            vehicle.tags.add(tag_obj)

    def _get_or_create_parts(self, parts, vehicle):
        """Handle getting or creating parts as needed."""
        auth_user = self.context['request'].user
        for part in parts:
            part_obj, created = Part.objects.get_or_create(
                user=auth_user,
                **part,
            )
            vehicle.parts.add(part_obj)

    def create(self, validated_data):
        """Create a vehicle."""
        tags = validated_data.pop('tags', [])
        parts = validated_data.pop('parts', [])
        vehicle = Vehicle.objects.create(**validated_data)
        self._get_or_create_tags(tags, vehicle)
        self._get_or_create_parts(parts, vehicle)

        return vehicle

    def update(self, instance, validated_data):
        """Update vehicle."""
        tags = validated_data.pop('tags', None)
        parts = validated_data.pop('parts', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if parts is not None:
            instance.parts.clear()
            self._get_or_create_parts(parts, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class VehicleDetailSerializer(VehicleSerializer):
    """Serializer for vehicle detail view"""

    class Meta(VehicleSerializer.Meta):
        fields = VehicleSerializer.Meta.fields + ['description']


class VehicleImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to vehicles."""

    class Meta:
        model = Vehicle
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
