import os
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.conf import settings
from statements.models import Transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scans email_support/ and imports new transactions into the database.'

    def handle(self, *args, **kwargs):
        root = getattr(settings, 'TRANSACTION_FILES_ROOT', 'email_support')
        
        if not os.path.exists(root):
            self.stderr.write(self.style.ERROR(f"Directory {root} does not exist."))
            return

        self.stdout.write(self.style.SUCCESS('Starting Transaction Import...'))
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for filename in os.listdir(root):
            filepath = os.path.join(root, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            try:
                # 1. Parse Filename: AccountNumber-TransactionID-YYMMDDHHMM
                # The filename doesn't have dashes between date/time, so it splits into 3 parts
                name_parts = filename.split('-')
                if len(name_parts) != 3:
                    raise ValueError("Invalid filename format")
                    
                account_number = name_parts[0]
                transaction_id = name_parts[1]
                
                # 2. Parse File Content
                with open(filepath, 'r') as f:
                    line = f.readline().strip()
                    content_parts = line.split('|')
                    
                    # Real files have at least 18 fields
                    if len(content_parts) < 18:
                        raise ValueError("Invalid file content format")
                        
                    status = content_parts[0] # DEBITED or CREDITED
                    # content_parts[1] is bank email, skip
                    # content_parts[4] is masked account number, so we use filename instead
                    
                    amount_str = content_parts[6]    # e.g., "NPR240.00"
                    date_str = content_parts[8]      # e.g., "10:14 22 AUG 2026"
                    description = content_parts[9]   # e.g., "debit"
                    operator = content_parts[10]     # e.g., "ESEWA.USER"
                    # content_parts[11] is Transaction ID, but we use filename to be safe
                    
                    email = content_parts[16]        # Customer Email
                    name = content_parts[17].strip() # Customer Name
                    
                # 3. Convert Data Types safely
                # Parse the date string into a Python datetime object
                txn_date = datetime.strptime(date_str, "%H:%M %d %b %Y")
                
                # Clean the amount string (remove 'NPR' if present, and any spaces)
                clean_amount = amount_str.replace("NPR", "").replace(" ", "").strip()
                amount = Decimal(clean_amount)
                
                # 4. Insert into Database (Prevent Duplicates)
                # get_or_create returns a tuple: (object, created_boolean)
                obj, created = Transaction.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        'account_number': account_number,
                        'transaction_type': status,
                        'amount': amount,
                        'transaction_date': txn_date,
                        'customer_name': name,
                        'customer_email': email,
                        'description': description,
                        'operator': operator,
                    }
                )
                
                if created:
                    imported_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported: {transaction_id}"))
                else:
                    skipped_count += 1
                    self.stdout.write(f"Skipped (already in DB): {transaction_id}")
                
                #  NEW REQUIREMENT: Delete the file immediately after DB success
                # This runs for BOTH newly imported and already-existing transactions,
                # because in both cases, the data is safely in the database.
                try:
                    os.remove(filepath)
                    self.stdout.write(f"  -> Deleted file: {filename}")
                except Exception as del_e:
                    self.stderr.write(self.style.ERROR(f"  -> Failed to delete file {filename}: {del_e}"))
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error importing file {filename}: {e}")
                self.stderr.write(self.style.ERROR(f"Failed to import {filename}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(
            f"\nImport Complete. Imported: {imported_count} | Skipped: {skipped_count} | Errors: {error_count}"
        ))