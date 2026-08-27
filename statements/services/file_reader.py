from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from statements.models import Transaction


def read_transactions(account_number, from_date, to_date):
    """
    Read transactions from the database for statement generation.

    Account matching:
        account_number_1 OR account_number_2

    Date matching:
        from_date 00:00:00 inclusive
        to_date + 1 day 00:00:00 exclusive

    Both CREDITED and DEBITED transactions are returned.
    """

    # ---------------------------------------------------------
    # Validate date range
    # ---------------------------------------------------------

    if from_date > to_date:
        return []

    account_number = str(account_number).strip()

    # ---------------------------------------------------------
    # Create timezone-aware datetime boundaries
    #
    # Example:
    #
    # from_date = 2026-08-26
    # to_date   = 2026-08-26
    #
    # Start:
    # 2026-08-26 00:00:00 +05:45
    #
    # End:
    # 2026-08-27 00:00:00 +05:45
    # ---------------------------------------------------------

    from_dt = timezone.make_aware(
        datetime.combine(
            from_date,
            time.min
        )
    )

    to_dt = timezone.make_aware(
        datetime.combine(
            to_date + timedelta(days=1),
            time.min
        )
    )

    # ---------------------------------------------------------
    # Query transactions
    #
    # IMPORTANT:
    # Match account_number against BOTH fields.
    #
    # There is intentionally NO status filter.
    #
    # Therefore:
    #   CREDITED -> included
    #   DEBITED  -> included
    # ---------------------------------------------------------

    queryset = (
        Transaction.objects
        .filter(
            Q(account_number_1=account_number)
            | Q(account_number_2=account_number),
            date_time__gte=from_dt,
            date_time__lt=to_dt,
        )
        .order_by("date_time")
    )

    # ---------------------------------------------------------
    # Convert database records to dictionaries
    # ---------------------------------------------------------

    transactions = []

    for txn in queryset:

        transactions.append({
            "Status": txn.status,
            "Email": txn.email,
            "Details_1": txn.details_1,
            "Account_Name": txn.account_name,
            "Masked_Account": txn.masked_account,
            "Details_2": txn.details_2,
            "Amount": str(txn.amount),
            "Fees": str(txn.fees),

            # Convert database timezone to Kathmandu time
            # before writing the statement.
            "Date_Time": timezone.localtime(
                txn.date_time
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "Details_3": txn.details_3,
            "User": txn.user,
            "File_Transaction_ID": txn.file_transaction_id,
            "Account_Number_1": txn.account_number_1,
            "Account_Number_2": txn.account_number_2,
            "Channel_Type": txn.channel_type,
            "ID": txn.id_value,
            "Payment_Details_2": txn.payment_details_2,
            "Customer_Details": txn.customer_details,
        })

    return transactions