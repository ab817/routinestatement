import csv
import os
import glob
from datetime import datetime


def parse_filename(filename):
    parts = filename.split('-')
    account_number = parts[0]  # Keep as string to preserve leading zeros
    transaction_id = parts[1]
    date_time = parts[2]

    # Convert date_time format (2502031444 -> 03 Feb 2025, 14:44)
    year = "20" + date_time[:2]
    month = date_time[2:4]
    day = date_time[4:6]
    hour = date_time[6:8]
    minute = date_time[8:]

    formatted_date_time = f"{day} {get_month_name(month).upper()} {year}, {hour}:{minute}"
    return account_number, transaction_id, formatted_date_time, date_time, f"{year}-{month}-{day}"


def get_month_name(month):
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    return months.get(month, "")


def parse_content(content):
    fields = content.strip().split('|')
    return {
        "Status": fields[0],
        "Email": fields[1],
        "Name": fields[2],
        "Account Number": fields[3],
        "Remarks 1": fields[4],
        "Amount": fields[5].replace("NPR", ""),  # Remove 'NPR' from amount
        "Fee": fields[6],
        "Date Time": fields[7],
        "Description": fields[8],
        "Remarks 2": fields[9],
        "Transaction ID": fields[10],
        "Debit Account": fields[11],
        "Credit Account": fields[12]
    }


def write_to_csv(account_number, records):
    timestamp = datetime.now().strftime("%Y%m%d")
    csv_filename = f"{account_number}_statement_{timestamp}.csv"
    headers = [
        "Status", "Email", "Name", "Account Number", "Remarks 1",
        "Amount", "Date Time", "Description", "Remarks 2", "Transaction ID",
        "Debit Account", "Credit Account"
    ]

    records.sort(key=lambda x: x["Raw Date Time"])  # Sort by timestamp

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for data in records:
            writer.writerow({
                key: f"'{data[key]}" if key in ["Debit Account", "Credit Account"] else data[key]
                for key in headers
            })  # Force string format for debit and credit account numbers

    print(f"CSV file '{csv_filename}' created successfully.")


# Process all relevant files in emailsupport directory
file_pattern = "email_support/0100200052107012-*"
files = glob.glob(file_pattern)
all_records = []
account_number = "0100200052107012"
system_date = datetime.now().strftime("%Y-%m-%d")

for filename in files:
    with open(filename, "r") as file:
        content = file.read()

    account_number, transaction_id, formatted_date_time, raw_date_time, file_date = parse_filename(
        os.path.basename(filename))

    if file_date == system_date:  # Only process today's records
        data = parse_content(content)
        data["Date Time"] = formatted_date_time
        data["Raw Date Time"] = raw_date_time  # Keep raw format for sorting
        all_records.append(data)

if all_records:
    write_to_csv(account_number, all_records)
else:
    print("No transactions found for today's date.")
