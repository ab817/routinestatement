from datetime import datetime
import os
import re


def parse_filename(filename):
    """
    Parse transaction filename.

    Expected format:

        ACCOUNT_NUMBER-TRANSACTION_ID-YYMMDDHHMM.txt

    Example:

        0100100003848029-FT262362B8RX-2608241649.txt

    Returns:
        {
            "account_no": "0100100003848029",
            "transaction_id": "FT262362B8RX",
            "datetime": datetime(2026, 8, 24, 16, 49)
        }

    Returns None if the filename format is invalid.
    """

    name, ext = os.path.splitext(filename)

    # Only process text files
    # If an extension exists, it must be .txt
    if ext and ext.lower() != ".txt":
        return None

    parts = name.split("-")

    if len(parts) != 3:
        return None

    account_no = parts[0].strip()
    transaction_id = parts[1].strip()
    date_part = parts[2].strip()

    if not account_no:
        return None

    if not transaction_id:
        return None

    # YYMMDDHHMM = exactly 10 digits
    if len(date_part) != 10 or not date_part.isdigit():
        return None

    try:
        year = int("20" + date_part[0:2])
        month = int(date_part[2:4])
        day = int(date_part[4:6])
        hour = int(date_part[6:8])
        minute = int(date_part[8:10])

        txn_datetime = datetime(
            year,
            month,
            day,
            hour,
            minute
        )

    except ValueError:
        return None

    return {
        "account_no": account_no,
        "transaction_id": transaction_id,
        "datetime": txn_datetime,
    }


def parse_transaction_line(line):
    """
    Parse a transaction file line.

    Expected source structure: exactly 18 fields separated by '|'.

    Returns a dictionary containing all 18 fields.
    """

    parts = line.strip().split("|")

    if len(parts) != 18:
        raise ValueError(
            f"Invalid transaction format. "
            f"Expected 18 fields, received {len(parts)}."
        )

    return {
        "status": parts[0].strip(),
        "email": parts[1].strip(),
        "details_1": parts[2].strip(),
        "account_name": parts[3].strip(),
        "masked_account": parts[4].strip(),
        "details_2": parts[5].strip(),
        "amount": parts[6].strip(),
        "fees": parts[7].strip(),
        "date_time": parts[8].strip(),
        "details_3": parts[9].strip(),
        "user": parts[10].strip(),
        "file_transaction_id": parts[11].strip(),
        "account_number_1": parts[12].strip(),
        "account_number_2": parts[13].strip(),
        "channel_type": parts[14].strip(),
        "id_value": parts[15].strip(),
        "payment_details_2": parts[16].strip(),
        "customer_details": parts[17].strip(),
    }


def parse_amount(value):
    """
    Normalize transaction amount/fee values into a
    Decimal-compatible string.

    Supported examples:

        NPR2000.00
        NPR 2000.00
        USD600000.00
        USD 22161.60
        2000.00
        1,234,567.89
        USD1,234.50

    Returns:
        A numeric string suitable for Decimal().
    """

    if value is None:
        return "0.00"

    value = str(value).strip()

    if not value:
        return "0.00"

    # Remove a 3-letter currency code only when it appears
    # at the beginning of the value.
    #
    # Examples:
    #   NPR2000.00  -> 2000.00
    #   USD6000.00  -> 6000.00
    #   EUR 500.00  -> 500.00
    #
    value = re.sub(
        r"^[A-Za-z]{3}\s*",
        "",
        value
    )

    # Remove thousands separators.
    value = value.replace(",", "")

    value = value.strip()

    if not value:
        return "0.00"

    # Validate the final value before passing it to Decimal().
    #
    # Accepted:
    #   2000
    #   2000.00
    #   -2000.00
    #   +2000.00
    #
    # Rejected:
    #   20ABC00
    #   USD20XYZ
    #   2,000.00 after malformed processing
    if not re.fullmatch(
        r"[+-]?\d+(?:\.\d+)?",
        value
    ):
        raise ValueError(
            f"Invalid amount format: {value}"
        )

    return value


def parse_transaction_datetime(value):
    """
    Convert source date format:

        16:49 24 AUG 2026

    into a Python datetime object.
    """

    if not value:
        raise ValueError("Transaction date/time is empty.")

    value = value.strip()

    try:
        return datetime.strptime(
            value,
            "%H:%M %d %b %Y"
        )

    except ValueError as exc:
        raise ValueError(
            f"Invalid transaction date/time: {value}"
        ) from exc