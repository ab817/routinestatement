import logging
from django.conf import settings
from django.core.mail import send_mail
from statements.models import Transaction
from alert.models import AlertMessage

logger = logging.getLogger(__name__)

def process_pending_alerts():
    logger.info("Starting Alert Routine: Checking database for pending alerts...")
    
    # 1. Get all transactions from the database
    transactions = Transaction.objects.all()
    
    sent_count = 0
    excluded_count = 0
    skipped_count = 0
    failed_count = 0
    
    for txn in transactions:
        # 2. Check if an alert was ALREADY recorded for this transaction
        # If an AlertMessage exists, we skip it entirely (prevents duplicate emails)
        if AlertMessage.objects.filter(transaction=txn).exists():
            skipped_count += 1
            continue
            
        # 3. Check if the account is EXCLUDED
        if txn.account_number in settings.EXCLUDED_ACCOUNTS:
            AlertMessage.objects.create(
                transaction=txn,
                recipient_email=txn.customer_email,
                status='EXCLUDED',
                error_info='Account is in the exclusion list.'
            )
            excluded_count += 1
            logger.info(f"Transaction {txn.transaction_id}: Account {txn.account_number} is excluded. Skipping email.")
            continue
            
        # 4. Prepare and Send the Email
        subject = "Transaction Alert"
        message = (
            f"Dear {txn.customer_name},\n\n"
            f"A transaction has occurred on your account.\n\n"
            f"Account Number: {txn.account_number}\n"
            f"Transaction Type: {txn.transaction_type}\n"
            f"Amount: NPR {txn.amount}\n\n"
            f"Thank you."
        )
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [txn.customer_email],
                fail_silently=False,
            )
            # 5. Record SUCCESS in the AlertMessage table
            AlertMessage.objects.create(
                transaction=txn,
                recipient_email=txn.customer_email,
                status='SENT'
            )
            sent_count += 1
            logger.info(f"Email sent successfully to {txn.customer_email} for transaction {txn.transaction_id}.")
            
        except Exception as e:
            # 5. Record FAILURE in the AlertMessage table
            AlertMessage.objects.create(
                transaction=txn,
                recipient_email=txn.customer_email,
                status='FAILED',
                error_info=str(e)
            )
            failed_count += 1
            logger.error(f"Failed to send email for {txn.transaction_id}: {e}")
            
    logger.info(f"Alert Routine Complete. Sent: {sent_count} | Excluded: {excluded_count} | Skipped: {skipped_count} | Failed: {failed_count}")