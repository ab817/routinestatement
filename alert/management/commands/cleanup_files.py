import os
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from statements.models import Transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Deletes transaction files in email_support older than the retention period, ONLY if they are in the database.'

    def handle(self, *args, **kwargs):
        root = getattr(settings, 'TRANSACTION_FILES_ROOT', 'email_support')
        retention_days = getattr(settings, 'TRANSACTION_FILE_RETENTION_DAYS', 2)
        
        if not os.path.exists(root):
            self.stderr.write(self.style.ERROR(f"Directory {root} does not exist."))
            return

        self.stdout.write(self.style.WARNING(f'Starting File Cleanup Routine (Retention: {retention_days} days)...'))
        
        threshold_dt = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        protected_count = 0
        
        for filename in os.listdir(root):
            filepath = os.path.join(root, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            try:
                # 1. Parse the date from the filename
                name_parts = filename.split('-')
                if len(name_parts) != 3:
                    continue  # Skip invalid formats
                    
                transaction_id = name_parts[1]
                datetime_str = name_parts[2]
                file_dt = datetime.strptime(datetime_str, "%y%m%d%H%M")
                
                # 2. Check if the file is older than the threshold
                if file_dt < threshold_dt:
                    
                    # 3. SAFETY CHECK: Is this transaction in the database?
                    is_in_database = Transaction.objects.filter(transaction_id=transaction_id).exists()
                    
                    if is_in_database:
                        # Safe to delete! The database has the record.
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {filename} (Already in DB)")
                    else:
                        # NOT safe to delete! We would lose this data forever.
                        protected_count += 1
                        logger.warning(f"Protected file (NOT in DB): {filename} - Skipping deletion.")
                        
            except Exception as e:
                logger.error(f"Error parsing date for cleanup of file {filename}: {e}")
            
        self.stdout.write(self.style.SUCCESS(
            f'Cleanup Complete. Deleted: {deleted_count} | Protected (Not in DB): {protected_count}'
        ))