"""
URL mappings for the vehicle app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from vehicle import views

router = DefaultRouter()
router.register('vehicles', views.VehicleViewSet)
router.register('tags', views.TagViewSet)

app_name = 'vehicle'

urlpatterns = [
    path('', include(router.urls))
]
