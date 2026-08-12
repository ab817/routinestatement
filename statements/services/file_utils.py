from datetime import datetime
import os

def parse_filename(filename):
    """
    123456789-TXN987654-20260101_143210.txt
    """
    name, ext = os.path.splitext(filename)
    parts = name.split("-")

    if len(parts) != 3:
        return None

    account_no = parts[0].strip()
    txn_id = parts[1].strip()
    date_part = parts[2].strip()

    # date_part must be exactly 10 digits: YYMMDDHHMM
    if len(date_part) != 10 or not date_part.isdigit():
        return None

    try:
        year = int("20" + date_part[0:2])   # 26 → 2026
        month = int(date_part[2:4])         # 01
        day = int(date_part[4:6])           # 20
        hour = int(date_part[6:8])          # 16
        minute = int(date_part[8:10])       # 55

        txn_datetime = datetime(year, month, day, hour, minute)
    except ValueError:
        return None

    return {
        "account_no": account_no,
        "transaction_id": txn_id,
        "datetime": txn_datetime
    }