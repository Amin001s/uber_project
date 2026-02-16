from django.db import models
from django.db.models import Q
from django.db.models.constraints import CheckConstraint

class BronzeLayer(models.Model):

    booking_id = models.CharField(max_length=100, primary_key=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    booking_status = models.CharField(max_length=100, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    
    cancelled_rides_by_customer = models.SmallIntegerField(null=True, blank=True)
    reason_for_cancelling_by_customer = models.TextField(null=True, blank=True)
    cancelled_rides_by_driver = models.SmallIntegerField(null=True, blank=True)
    driver_cancellation_reason = models.TextField(null=True, blank=True)
    

    incomplete_rides = models.SmallIntegerField(null=True, blank=True)
    incomplete_rides_reason = models.TextField(null=True, blank=True)
    
    booking_value = models.FloatField(null=True, blank=True)
    ride_distance = models.FloatField(null=True, blank=True)
    

    driver_ratings = models.FloatField(null=True, blank=True)
    customer_rating = models.FloatField(null=True, blank=True)
    
    payment_method = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = '"bronze"."raw_dataset"'
        managed = True



class SilverLayer(models.Model):
    booking_id = models.CharField(max_length=100, primary_key=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    day_of_week = models.CharField(max_length=20, null=True)
    
    booking_status = models.CharField(max_length=100, null=True)
    customer_id = models.CharField(max_length=100, null=True)
    vehicle_type = models.CharField(max_length=100, null=True)
    
    cancelled_rides_by_driver = models.SmallIntegerField(default=0)
    cancelled_rides_by_customer = models.SmallIntegerField(default=0)
    incomplete_rides = models.SmallIntegerField(default=0)
    unified_cancellation_reason = models.TextField(null=True)
    booking_value = models.FloatField(null=True, blank=True)
    ride_distance = models.FloatField(null=True, blank=True)
    driver_ratings = models.FloatField(null=True)
    customer_rating = models.FloatField(null=True)
    payment_method = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = '"silver"."cleaned_dataset"'
        managed = True


class GoldLayer(models.Model):
    booking_id = models.CharField(max_length=100, primary_key=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    day_of_week = models.CharField(max_length=20, null=True)
    booking_status = models.CharField(max_length=100, null=True)
    customer_id = models.CharField(max_length=100, null=True)
    vehicle_type = models.CharField(max_length=100, null=True)

    cancelled_rides_by_driver = models.SmallIntegerField(default=0)
    cancelled_rides_by_customer = models.SmallIntegerField(default=0)
    incomplete_rides = models.SmallIntegerField(default=0)
    unified_cancellation_reason = models.TextField(null=True)
    
    booking_value = models.FloatField(null=True, blank=True)
    ride_distance = models.FloatField(null=True, blank=True)
    revenue_per_km = models.FloatField(null=True, blank=True)
    
    driver_ratings = models.FloatField(null=True)
    customer_rating = models.FloatField(null=True)
    payment_method = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = '"gold"."dataset"'
        managed = True
        
        #محدودیت ها
        constraints = [
            
            CheckConstraint(
                check=Q(driver_ratings__gte=0) & Q(driver_ratings__lte=5) | Q(driver_ratings__isnull=True),
                name='driver_rating_range'
            ),
            CheckConstraint(
                check=Q(customer_rating__gte=0) & Q(customer_rating__lte=5) | Q(customer_rating__isnull=True),
                name='customer_rating_range'
            ),
        ]