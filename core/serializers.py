from rest_framework import serializers
from .models import GoldLayer

class GoldLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldLayer
        fields = '__all__'
        read_only_fields = ['booking_id']