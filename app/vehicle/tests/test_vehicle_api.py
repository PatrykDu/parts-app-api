"""
Tests for vehicle APIs.
"""
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Vehicle,
    Tag,
    Part
)

from vehicle.serializers import (
    VehicleSerializer,
    VehicleDetailSerializer,
)


VEHICLES_URL = reverse('vehicle:vehicle-list')


def detail_url(vehicle_id):
    """Create and return a vehicle detail URL."""
    return reverse('vehicle:vehicle-detail', args=[vehicle_id])


def image_upload_url(vehicle_id):
    """Create and return an image upload URL."""
    return reverse('vehicle:vehicle-upload-image', args=[vehicle_id])


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

        url = detail_url(vehicle.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Vehicle.objects.filter(id=vehicle.id).exists())

    def test_create_vehicle_with_new_tags(self):
        """Test creating a vehicle with new tags."""
        payload = {
            'title': 'BMW R100',
            'year': 1980,
            'price': 4000,
            'tags': [{'name': 'Motorcycle'}, {'name': 'Classic'}],
        }
        res = self.client.post(VEHICLES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        vehicles = Vehicle.objects.filter(user=self.user)
        self.assertEqual(vehicles.count(), 1)
        vehicle = vehicles[0]
        self.assertEqual(vehicle.tags.count(), 2)
        for tag in payload['tags']:
            exists = vehicle.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_vehicle_with_existing_tags(self):
        """Test creating a vehicle with existing tag."""
        tag_car = Tag.objects.create(user=self.user, name='car')
        payload = {
            'title': 'Mazda MX-5',
            'year': 1992,
            'price': 12000,
            'tags': [{'name': 'car'}, {'name': 'classic'}],
        }
        res = self.client.post(VEHICLES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        vehicles = Vehicle.objects.filter(user=self.user)
        self.assertEqual(vehicles.count(), 1)
        vehicle = vehicles[0]
        self.assertEqual(vehicle.tags.count(), 2)
        self.assertIn(tag_car, vehicle.tags.all())
        for tag in payload['tags']:
            exists = vehicle.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test create tag when updating a vehicle."""
        vehicle = create_vehicle(user=self.user)

        payload = {'tags': [{'name': 'car'}]}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='car')
        self.assertIn(new_tag, vehicle.tags.all())

    def test_update_vehicle_assign_tag(self):
        """Test assigning an existing tag when updating a vehicle."""
        tag_motorcycle = Tag.objects.create(user=self.user, name='modern')
        vehicle = create_vehicle(user=self.user)
        vehicle.tags.add(tag_motorcycle)

        tag_classic = Tag.objects.create(user=self.user, name='classic')
        payload = {'tags': [{'name': 'classic'}]}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_classic, vehicle.tags.all())
        self.assertNotIn(tag_motorcycle, vehicle.tags.all())

    def test_clear_vehicle_tags(self):
        """Test clearing a vehicles tags."""
        tag = Tag.objects.create(user=self.user, name='testtag')
        vehicle = create_vehicle(user=self.user)
        vehicle.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(vehicle.tags.count(), 0)

    def test_create_vehicle_with_new_parts(self):
        """Test creating a vehicle with new parts."""
        payload = {
            'title': 'Mazda MX-5',
            'year': 1992,
            'price': 12000,
            'parts': [
                {'name': 'exhaust', 'price': 1500},
                {'name': 'wheels', 'price': 1500}
            ],
        }
        res = self.client.post(VEHICLES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        vehicles = Vehicle.objects.filter(user=self.user)
        self.assertEqual(vehicles.count(), 1)
        vehicle = vehicles[0]
        self.assertEqual(vehicle.parts.count(), 2)
        for part in payload['parts']:
            exists = vehicle.parts.filter(
                name=part['name'],
                price=part['price'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_vehicle_with_existing_part(self):
        """Test creating a new vehicle with existing part."""
        part = Part.objects.create(user=self.user, name='Kardan', price=1000)
        payload = {
            'title': 'BMW R100',
            'year': 1991,
            'price': 5000,
            'parts': [
                {'name': 'Kardan', 'price': 1000},
                {'name': 'Engine', 'price': 1500}
            ],
        }
        res = self.client.post(VEHICLES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        vehicles = Vehicle.objects.filter(user=self.user)
        self.assertEqual(vehicles.count(), 1)
        vehicle = vehicles[0]
        self.assertEqual(vehicle.parts.count(), 2)
        self.assertIn(part, vehicle.parts.all())
        for part in payload['parts']:
            exists = vehicle.parts.filter(
                name=part['name'],
                user=self.user,
                price=part['price'],
            ).exists()
            self.assertTrue(exists)

    def test_create_part_on_update(self):
        """Test creating an part when updating a vehicle."""
        vehicle = create_vehicle(user=self.user)

        payload = {'parts': [{'name': 'gearbox', 'price': 500}]}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_part = Part.objects.get(user=self.user, name='gearbox', price=500)
        self.assertIn(new_part, vehicle.parts.all())

    def test_update_vehicle_assign_part(self):
        """Test assigning an existing part when updating a vehicle."""
        part1 = Part.objects.create(user=self.user, name='wheels', price=1500)
        vehicle = create_vehicle(user=self.user)
        vehicle.parts.add(part1)

        part2 = Part.objects.create(user=self.user, name='Tyres', price=400)
        payload = {'parts': [{'name': 'Tyres', 'price': 400}]}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(part2, vehicle.parts.all())
        self.assertNotIn(part1, vehicle.parts.all())

    def test_clear_vehicle_parts(self):
        """Test clearing a vehicles parts."""
        part = Part.objects.create(user=self.user, name='Fenders', price=300)
        vehicle = create_vehicle(user=self.user)
        vehicle.parts.add(part)

        payload = {'parts': []}
        url = detail_url(vehicle.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(vehicle.parts.count(), 0)


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.vehicle = create_vehicle(user=self.user)

    def tearDown(self):
        self.vehicle.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a vehicle."""
        url = image_upload_url(self.vehicle.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.vehicle.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.vehicle.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.vehicle.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
