"""
Tests for vehicle APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Vehicle

from vehicle.serializers import (
    VehicleSerializer,
    VehicleDetailSerializer,
)


VEHICLES_URL = reverse('vehicle:vehicle-list')


def detail_url(vehicle_id):
    """Create and return a vehicle detail URL."""
    return reverse('vehicle:vehicle-detail', args=[vehicle_id])


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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicVehicleAPITests(TestCase):
    """Test unaunthicated API requests."""

    def setUp(self) -> None:
        # test client we can use for tests added to this class
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is requied to call API"""
        res = self.client.get(VEHICLES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVehicleAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
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
        """Test list of vehicles is limited to authenticated user."""
        other_user = create_user(
            email='other@example.com', password='test123')
        create_vehicle(user=other_user)
        create_vehicle(user=self.user)

        res = self.client.get(VEHICLES_URL)

        vehicles = Vehicle.objects.filter(user=self.user)
        serializer = VehicleSerializer(vehicles, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_vehicle_detail(self):
        """Test get vehicle detail."""
        vehicle = create_vehicle(user=self.user)

        url = detail_url(vehicle.id)
        res = self.client.get(url)

        serializer = VehicleDetailSerializer(vehicle)
        self.assertEqual(res.data, serializer.data)

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        payload = {
            'title': 'Sample vehicle',
            'year': 2020,
            'price': 150000
        }
        res = self.client.post(VEHICLES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        vehicle = Vehicle.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(vehicle, k), v)
        self.assertEqual(vehicle.user, self.user)

    def test_partial_update(self):
        """Test partial update of a vehicle."""
        original_link = 'https://example.com/vehicle.pdf'
        vehicle = create_vehicle(
            user=self.user,
            title='Sample vehicle title',
            link=original_link
        )

        payload = {'title': 'New vehicle title'}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        self.assertEqual(vehicle.title, payload['title'])
        self.assertEqual(vehicle.link, original_link)
        self.assertEqual(vehicle.user, self.user)

    def test_full_update(self):
        """Test full update of vehicle."""
        vehicle = create_vehicle(
            user=self.user,
            title='Sample vehicle title',
            link='https://example.com/vehicle.pdf',
            description='Sample vehicle description',
        )

        payload = {
            'title': 'New vehicle title',
            'link': 'https://example.com/new-vehicle.pdf',
            'description': 'New sample vehicle description',
            'year': 2022,
            'price': 180000
        }
        url = detail_url(vehicle.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        vehicle.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(vehicle, k), v)
        self.assertEqual(vehicle.user, self.user)

    def test_update_user_returns_error(self):
        """Test changigng the vehicle user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        vehicle = create_vehicle(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(vehicle.id)
        self.client.patch(url, payload)

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.user, self.user)

    def test_delete_vehicle(self):
        """Test deleting a vehicle successful."""
        vehicle = create_vehicle(user=self.user)

        url = detail_url(vehicle.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Vehicle.objects.filter(id=vehicle.id).exists())

    def test_vehicle_other_user_vehicle_error(self):
        """Test trying to delete another users vehicle gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        vehicle = create_vehicle(user=new_user)

        url = detail_url(Vehicle.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Vehicle.objects.filter(id=vehicle.id).exists())
