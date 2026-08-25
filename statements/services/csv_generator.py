import csv
from io import StringIO

def generate_csv(transactions):
    output = StringIO()

    fieldnames = [
        "Status", "Email", "Name", "Account Number", "Remarks 1",
        "Amount", "Fee", "Date", "Description", "Remarks 2",
        "Transaction ID", "Debit Account", "Credit Account",
        "Details 1", "Details 2", "Details 3"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for txn in transactions:
        row = txn.copy()
        
        # Force Excel to keep Account Number as text
        if row.get("Account Number"):
            row["Account Number"] = f'="{row["Account Number"]}"'

        

        writer.writerow(row)

    return output.getvalue()
