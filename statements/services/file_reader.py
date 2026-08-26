from datetime import datetime

from statements.models import Transaction


def read_transactions(account_number, from_date, to_date):
    """
    Read transactions from the database.

    The source files are imported into the database first and may then
    be deleted. Therefore, API transaction lookup should use the database.

    Parameters:
        account_number:
            Account number to search.

        from_date:
            Python date object representing the starting date.

        to_date:
            Python date object representing the ending date.

    Returns:
        List of transaction dictionaries.
    """

    # ---------------------------------------------------------
    # Inclusive date range
    # ---------------------------------------------------------

    from_dt = datetime.combine(
        from_date,
        datetime.min.time()
    )

    to_dt = datetime.combine(
        to_date,
        datetime.max.time()
    )

    # ---------------------------------------------------------
    # Query database
    #
    # Account_Number_2 is used as the primary account number
    # for the API transaction lookup.
    # ---------------------------------------------------------

    queryset = (
        Transaction.objects
        .filter(
            account_number_2=str(account_number),
            date_time__gte=from_dt,
            date_time__lte=to_dt,
        )
        .order_by("date_time")
    )

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
            "Date_Time": txn.date_time.strftime(
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