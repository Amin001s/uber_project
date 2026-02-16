from django.core.management.base import BaseCommand
from core.models import SilverLayer, GoldLayer
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        GoldLayer.objects.all().delete()
        
        silver_data = SilverLayer.objects.all().iterator(chunk_size=5000)
        
        objs = []
        batch_size = 5000
        count = 0
        print("Starting the process")
        for row in silver_data:
            
            rev_per_km = None
            
            # »حاسبه ارزش بر مسافت
            if row.booking_value and row.ride_distance and row.ride_distance > 0:
                val = row.booking_value / row.ride_distance
                rev_per_km=round(val, 2)
            else:
                rev_per_km = None


            objs.append(GoldLayer(
                booking_id=row.booking_id,
                date=row.date,
                time=row.time,
                day_of_week=row.day_of_week,
                booking_status=row.booking_status,
                customer_id=row.customer_id,
                vehicle_type=row.vehicle_type,
                cancelled_rides_by_driver=row.cancelled_rides_by_driver,
                cancelled_rides_by_customer=row.cancelled_rides_by_customer,
                incomplete_rides=row.incomplete_rides,
                unified_cancellation_reason=row.unified_cancellation_reason,
                booking_value=row.booking_value,
                ride_distance=row.ride_distance,
                revenue_per_km=rev_per_km,
                
                driver_ratings=row.driver_ratings,
                customer_rating=row.customer_rating,
                payment_method=row.payment_method
            ))

            if len(objs) >= batch_size:
                GoldLayer.objects.bulk_create(objs, ignore_conflicts=True)
                count += len(objs)
                print(f"{count} rows added")
                objs = []

        if objs:
            GoldLayer.objects.bulk_create(objs, ignore_conflicts=True)
        
        print("Finished!")