import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from core.models import BronzeLayer

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        BronzeLayer.objects.all().delete()
        file_path = 'Database.csv'
        
        
            
        df = pd.read_csv(file_path, engine='python')

        print("Starting the process")

        #تبدیل تاریخ
        def parse_date(value):
            if pd.isna(value):
                return None
            
            return pd.to_datetime(value).date()
            
            
        #تبدیل رشته به زمان معتبر
        def parse_time(value):
            if pd.isna(value):
                return None

            return pd.to_datetime(str(value), format='%H:%M:%S', errors='coerce').time()

        #هندل کردن Null
        def clean(value):
            if pd.isna(value):
                return None

            s_val = str(value).strip().lower()
            
            if s_val == 'null':
                return None

            return value

        batch_size = 5000
        objs = []
        
        #ذخیره
        for index, row in df.iterrows():
    
            b_id = clean(row.get('Booking ID'))
            if not b_id:
                continue

            objs.append(BronzeLayer(
                booking_id=b_id,
                
                date=parse_date(row.get('Date')),
                time=parse_time(row.get('Time')),
                booking_status=clean(row.get('Booking Status')),
                customer_id=clean(row.get('Customer ID')),
                vehicle_type=clean(row.get('Vehicle Type')),
                
                cancelled_rides_by_customer=clean(row.get('Cancelled Rides by Customer')),
                reason_for_cancelling_by_customer=clean(row.get('Reason for cancelling by Customer')),
                
                cancelled_rides_by_driver=clean(row.get('Cancelled Rides by Driver')),
                driver_cancellation_reason=clean(row.get('Driver Cancellation Reason')),
                
                incomplete_rides=clean(row.get('Incomplete Rides')),
                incomplete_rides_reason=clean(row.get('Incomplete Rides Reason')),
                
                
                booking_value=clean(row.get('Booking Value')),
                ride_distance=clean(row.get('Ride Distance')),
                
                driver_ratings=clean(row.get('Driver Ratings')),
                customer_rating=clean(row.get('Customer Rating')),
                
                payment_method=clean(row.get('Payment Method'))
            ))
            
            #ذخیره دسته ای
            if len(objs) >= batch_size:
                BronzeLayer.objects.bulk_create(objs, ignore_conflicts=True)
                print(f"{index + 1} rows added")
                objs = []
        
        # ذخیره باقیمانده‌ها
        if objs:
            BronzeLayer.objects.bulk_create(objs, ignore_conflicts=True)
            
        print(f"Finished")