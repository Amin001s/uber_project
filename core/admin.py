from django.contrib import admin
from .models import BronzeLayer, SilverLayer, GoldLayer

@admin.register(BronzeLayer)
class BronzeAdmin(admin.ModelAdmin):
    list_display = ('date', 'time',  'booking_id', 'booking_status', 'customer_id', 'vehicle_type', 'cancelled_rides_by_customer',
    'reason_for_cancelling_by_customer', 'cancelled_rides_by_driver', 'driver_cancellation_reason', 'incomplete_rides',
    'incomplete_rides_reason', 'booking_value', 'ride_distance', 'driver_ratings', 
    'customer_rating', 'payment_method')

    search_fields = ('booking_id', 'customer_id')

@admin.register(SilverLayer)
class SilverAdmin(admin.ModelAdmin):

    list_display = ('date', 'time','day_of_week', 'booking_id', 'booking_status', 'customer_id', 'vehicle_type',
    'unified_cancellation_reason', 'booking_value', 'ride_distance', 'driver_ratings', 'customer_rating', 'payment_method')
    
    list_filter = (
        'booking_status', 
        'vehicle_type'
    )
    

    search_fields = ('booking_id', 'customer_id')
    date_hierarchy = 'date'

@admin.register(GoldLayer)
class GoldAdmin(admin.ModelAdmin):
    list_display = ('date', 'time','day_of_week', 'booking_id', 'booking_status', 'customer_id', 'vehicle_type',
    'unified_cancellation_reason', 'booking_value', 'ride_distance', 'revenue_per_km', 'driver_ratings', 
    'customer_rating', 'payment_method',)
    list_filter = ('booking_status',)