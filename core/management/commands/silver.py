import pandas as pd
from django.core.management.base import BaseCommand
from core.models import BronzeLayer, SilverLayer

class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        SilverLayer.objects.all().delete()
        bronze_data = BronzeLayer.objects.all().iterator(chunk_size=5000)
        
        objs = []
        batch_size = 5000
        count = 0

        print("Starting the process")
        
        for row in bronze_data:

            final_date = None
            final_time = None
            day_name = None

            # پیدا کردن روز هفته
            if row.date:
                
                dt = pd.to_datetime(str(row.date).strip())
                final_date = dt.date()
                day_name = dt.day_name() 
                
            
            # تبدیل null به صفر
            def parse_int(value):
                if pd.isna(value):
                    return 0  
                
                return value
                

            
            unified_reason = None
            status = str(row.booking_status).lower() if row.booking_status else ""

            
            if (row.cancelled_rides_by_customer==1):
                unified_reason = row.reason_for_cancelling_by_customer
            elif (row.cancelled_rides_by_driver==1):
                unified_reason = row.driver_cancellation_reason
            elif (row.incomplete_rides==1):
                unified_reason = row.incomplete_rides_reason
            

            
            objs.append(SilverLayer(
                booking_id=row.booking_id.strip('"') if row.booking_id else None,
                
                
                date=final_date,
                time=row.time,
                day_of_week=day_name,
                booking_status=row.booking_status,
                customer_id=row.customer_id.strip('"') if row.booking_id else None,
                
                vehicle_type=row.vehicle_type,
                cancelled_rides_by_driver=parse_int(row.cancelled_rides_by_driver),
                cancelled_rides_by_customer=parse_int(row.cancelled_rides_by_customer),
                incomplete_rides=parse_int(row.incomplete_rides),
                unified_cancellation_reason=unified_reason,
                booking_value=row.booking_value,
                ride_distance=row.ride_distance,
                driver_ratings=row.driver_ratings,
                customer_rating=row.customer_rating,
                payment_method=row.payment_method
            ))

            
            if len(objs) >= batch_size:
                SilverLayer.objects.bulk_create(objs, ignore_conflicts=True)
                count += len(objs)
                print(f"{count} rows added")
                objs = []

        
        if objs:
            SilverLayer.objects.bulk_create(objs, ignore_conflicts=True)
            print(f"Total rows: {count + len(objs)} ")
            
        print("Finished!")