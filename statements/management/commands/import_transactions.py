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
                    
                    if len(content_parts) < 11:
                        raise ValueError("Invalid file content format")
                        
                    status = content_parts[0]       # CREDITED or DEBITED
                    email = content_parts[1]         # Recipient email
                    name = content_parts[2].strip()  # Customer name
                    amount_str = content_parts[5]    # Amount
                    date_str = content_parts[7]      # Date String (e.g., 20:36 04 FEB 2025)
                    description = content_parts[8]   # Description
                    operator = content_parts[9]      # Operator
                    
                # 3. Convert Data Types safely
                # Parse the date string into a Python datetime object
                # Example: "20:36 04 FEB 2025" -> "%H:%M %d %b %Y"
                txn_date = datetime.strptime(date_str, "%H:%M %d %b %Y")
                
                # Parse amount into Decimal
                amount = Decimal(amount_str)
                
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
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error importing file {filename}: {e}")
                self.stderr.write(self.style.ERROR(f"Failed to import {filename}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(
            f"\nImport Complete. Imported: {imported_count} | Skipped: {skipped_count} | Errors: {error_count}"
        ))