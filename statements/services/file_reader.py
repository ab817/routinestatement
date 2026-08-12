import os
from django.conf import settings
from datetime import datetime, timedelta
from .file_utils import parse_filename

def read_transactions(account_number, from_date, to_date):
    transactions = []

    # Make date range inclusive
    from_dt = datetime.combine(from_date, datetime.min.time())
    to_dt = datetime.combine(to_date, datetime.max.time())

    root = settings.TRANSACTION_FILES_ROOT

    for filename in os.listdir(root):
        try:
            meta = parse_filename(filename)
        except ValueError:
            continue
        
        if not meta:
            continue
        

        # Filter by account
        if str(meta["account_no"]) != str(account_number):
            continue


        # Filter by date range
        if not (from_dt <= meta["datetime"] <= to_dt):
            continue

        file_path = os.path.join(root, filename)

        with open(file_path, "r") as f:
            line = f.readline().strip()
            parts = line.split("|")

            if len(parts) < 6:
                continue

            txn = {
                "Status": parts[0],
                "Email": parts[1],
                "Name": parts[2],
                "Account Number": meta["account_no"],
                "Remarks 1": parts[4],
                "Amount": parts[5],  
                "Fee": parts[6],
                "Date": meta["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                "Description": parts[8],
                "Remarks 2": parts[9],
                "Transaction ID": meta["transaction_id"],
                "Debit Account": parts[11],
                "Credit Account": parts[12],
                "Details 1": parts[13],
                "Details 2": parts[14],
                "Details 3": parts[15],
                # "account_no": meta["account_no"],
                # "transaction_id": meta["transaction_id"],
                # "date": meta["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                # "amount": parts[3],
                # "type": parts[4],
                # "description": parts[5],
            }

            transactions.append(txn)

    # Optional: sort by datetime
    transactions.sort(key=lambda x: x["Date"])

    return transactions
