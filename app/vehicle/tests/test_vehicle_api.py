"""
Tests for vehicle APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Vehicle

from vehicle.serializers import VehicleSerializer


VEHICLES_URL = reverse('vehicle:vehicle-list')


def create_vehicle(user, **params):
    """Create and return a sample vehicle."""
    defaults = {
        'title': 'Sample vehicle title',
        'year': 2020,
        'price': 150000,
        'description': 'Sample description',
        'link': 'http://example.com/vehicle.pdf'
    }
    defaults.update(params)

    vehicle = Vehicle.objects.create(user=user, **defaults)
    return vehicle


class PublicVehicleAPITests(TestCase):
    """Test unaunthicated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()  # test client we can use for tests added to this class

    def test_auth_required(self):
        """Test auth is requied to call API"""
        res = self.client.get(VEHICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVehicleAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()  # test client we can use for tests added to this class
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        """Test auth is requied to call API"""
        res = self.client.get(VEHICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrive_vehicles(self):
        """Test retriving a list of vehicles."""
        create_vehicle(user=self.user)
        create_vehicle(user=self.user)

        res = self.client.get(VEHICLES_URL)

        vehicles = Vehicle.objects.all().order_by('-id')
        serializer = VehicleSerializer(vehicles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_vehicle_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'testpass123'
        )
        create_vehicle(user=other_user)
        create_vehicle(user=self.user)

        res = self.client.get(VEHICLES_URL)

        vehicles = Vehicle.objects.filter(user=self.user)
        serializer = VehicleSerializer(vehicles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
