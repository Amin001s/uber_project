from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoldLayerView


router = DefaultRouter()
router.register(r'trips', GoldLayerView, basename='trip')

urlpatterns = [
    path('', include(router.urls)),
]