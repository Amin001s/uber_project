from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import GoldLayer
from .serializers import GoldLayerSerializer
from django.db import connection 
import random

class GoldLayerView(viewsets.ModelViewSet):
    queryset = GoldLayer.objects.order_by('-date').all()
    serializer_class = GoldLayerSerializer
    lookup_field = 'booking_id'
    pagination_class = None

        #لیست سفر ها
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id.strip())

        raw_sql = str(queryset.query)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "data": serializer.data,
            "sql_query": raw_sql
        })

        
    #تولید عدد رندوم برای booking_id
    def perform_create(self, serializer):

        rand_num = random.randint(10000000, 99999999)
        generated_id = f"CNR{rand_num}"
        
        serializer.save(
            booking_id=generated_id,
            booking_status='Completed'
        )

    #ساخت سفر
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        last_query = connection.queries[-1]['sql']
        return Response({
            "data": response.data,
            "sql_query": last_query
        }, status=status.HTTP_201_CREATED)

    #اپدیت سفر
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        last_query = connection.queries[-1]['sql']
        return Response({
            "data": response.data,
            "sql_query": last_query
        }, status=status.HTTP_200_OK)

    # حذف سفر
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        last_query = connection.queries[-1]['sql']
        return Response({
            "message": "Deleted successfully",
            "sql_query": last_query
        }, status=status.HTTP_200_OK)
    
