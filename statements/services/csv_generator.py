import csv
from io import StringIO


def generate_csv(transactions):
    """
    Generate CSV output from transaction records.

    Expected transaction dictionary keys are the 18 source fields.
    """

    output = StringIO()

    fieldnames = [
        "Status",
        "Email",
        "Details_1",
        "Account_Name",
        "Masked_Account",
        "Details_2",
        "Amount",
        "Fees",
        "Date_Time",
        "Details_3",
        "User",
        "File_Transaction_ID",
        "Account_Number_1",
        "Account_Number_2",
        "Channel_Type",
        "ID",
        "Payment_Details_2",
        "Customer_Details",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )

    writer.writeheader()

    for txn in transactions:

        row = {}

        for field in fieldnames:
            value = txn.get(field, "")

            # -----------------------------------------------------
            # Keep account numbers as text when opened in Excel.
            #
            # This prevents Excel from removing leading zeros.
            # -----------------------------------------------------

            if field in (
                "Account_Number_1",
                "Account_Number_2",
                "Masked_Account",
            ):

                if value not in (None, ""):

                    value = f'="{value}"'

            row[field] = value

        writer.writerow(row)

    return output.getvalue()