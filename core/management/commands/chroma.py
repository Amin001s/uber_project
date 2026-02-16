import os
import chromadb
from django.conf import settings
from django.core.management.base import BaseCommand
from core.models import GoldUberData 

class Command(BaseCommand):
    def handle(self, *args, **options):

        queryset = GoldUberData.objects.exclude(
            unified_cancellation_reason__isnull=True
        ).exclude(
            unified_cancellation_reason__exact=''
        ).values('booking_id', 'unified_cancellation_reason')[:2000]

        data_list = list(queryset)
        total_rows = len(data_list)
        
        self.stdout.write(self.style.SUCCESS(f"Loaded {total_rows} records from Django Models."))


        chroma_path = os.path.join(settings.BASE_DIR, 'dashboard', 'chroma_db')
        os.makedirs(chroma_path, exist_ok=True)
        
        client = chromadb.PersistentClient(path=chroma_path)

        collection_name = "cancellation_reasons"


        try:
            client.delete_collection(name=collection_name)
            self.stdout.write(f"   Deleted existing collection '{collection_name}'")
        except Exception: 
            self.stdout.write(f"Collection '{collection_name}' did not exist. Creating new one.")


        collection = client.create_collection(name=collection_name)


        batch_size = 500
        
        for i in range(0, total_rows, batch_size):
            batch = data_list[i : i + batch_size]
            
            ids = [str(item['booking_id']) for item in batch]
            documents = [item['unified_cancellation_reason'] for item in batch]
            metadatas = [{"reason": item['unified_cancellation_reason']} for item in batch]

            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            

            current_count = min(i + batch_size, total_rows)
            self.stdout.write(f"Processed {current_count} / {total_rows} records...")

        print("Finished!")