"""
Tests for the parts API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Vehicle,
    Part,
)

from vehicle.serializers import PartSerializer


PARTS_URL = reverse('vehicle:part-list')


def detail_url(part_id):
    """Create and return an part detail URL."""
    return reverse('vehicle:part-detail', args=[part_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicPartsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving parts."""
        res = self.client.get(PARTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePartsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_parts(self):
        """Test retrieving a list of parts."""
        Part.objects.create(user=self.user, name='susspension', price=1400)
        Part.objects.create(user=self.user, name='splitter', price=150)

        res = self.client.get(PARTS_URL)

        parts = Part.objects.all().order_by('-name')
        serializer = PartSerializer(parts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_parts_limited_to_user(self):
        """Test list of parts is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Part.objects.create(user=user2, name='oil pump', price=400)
        part = Part.objects.create(
            user=self.user, name='forged pistons', price=800)

        res = self.client.get(PARTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], part.name)
        self.assertEqual(res.data[0]['id'], part.id)
        self.assertEqual(res.data[0]['price'], part.price)

    def test_update_part(self):
        """Test updating an part."""
        part = Part.objects.create(
            user=self.user, name='wheels', price=1600)

        payload = {'name': 'electricts', 'price': 2000}
        url = detail_url(part.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        part.refresh_from_db()
        self.assertEqual(part.name, payload['name'])
        self.assertEqual(part.price, payload['price'])

    def test_delete_part(self):
        """Test deleting an part."""
        part = Part.objects.create(user=self.user, name='exhaust', price=1500)

        url = detail_url(part.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        parts = Part.objects.filter(user=self.user)
        self.assertFalse(parts.exists())

    def test_filter_parts_assigned_to_vehicles(self):
        """Test listing parts to those assigned to vehicles."""
        part1 = Part.objects.create(
            user=self.user, name='headlights', price=500)
        part2 = Part.objects.create(user=self.user, name='engine', price=3000)
        vehicle = Vehicle.objects.create(
            title='mx5',
            year=1992,
            price=12000,
            user=self.user,
        )
        vehicle.parts.add(part1)

        res = self.client.get(PARTS_URL, {'assigned_only': 1})

        s1 = PartSerializer(part1)
        s2 = PartSerializer(part2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_parts_unique(self):
        """Test filtered parts returns a unique list."""
        part = Part.objects.create(user=self.user, name='wheels', price=1500)
        Part.objects.create(user=self.user, name='turbo', price=400)
        vehicle1 = Vehicle.objects.create(
            title='mx5',
            year=1992,
            price=12000,
            user=self.user,
        )
        vehicle2 = Vehicle.objects.create(
            title='r100',
            year=1991,
            price=5000,
            user=self.user,
        )
        vehicle1.parts.add(part)
        vehicle2.parts.add(part)

        res = self.client.get(PARTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
