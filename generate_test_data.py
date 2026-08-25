import os
from datetime import datetime, timedelta
import random

# Configuration
OUTPUT_DIR = "email_support"  # The folder where your Django app reads the files
TOTAL_ACCOUNTS = 1
TXNS_PER_ACCOUNT_PER_DAY = 1

# 5 Fake 16-digit account numbers
FAKE_ACCOUNTS = [
    
    "0100200000008032",
]

# Some dummy names and emails to make the data look real
DUMMY_NAMES = [
    ("NITA KOIRALA", "manishacharya3345@gmail.com"),
    
    
]

def generate_files():
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Generating test data in '{OUTPUT_DIR}' folder...")
    
    # The two dates we need: Yesterday and Today
    dates_to_generate = [
        datetime.now() - timedelta(days=1), # Yesterday
        datetime.now()                       # Today
    ]
    
    txn_counter = 5710  # Just a starting point for the transaction ID

    for acc_num in FAKE_ACCOUNTS:
        for target_date in dates_to_generate:
            for i in range(TXNS_PER_ACCOUNT_PER_DAY):
                txn_counter += 1
                
                # 1. Generate a random time during that day
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                txn_datetime = target_date.replace(hour=random_hour, minute=random_minute, second=0)
                
                # 2. Generate the Transaction ID (e.g., DC250145241003004)
                # Using the counter to ensure it's unique
                txn_id = f"DC{txn_counter:015d}"
                
                # 3. Format the filename: AccountNumber-TransactionID-YYMMDDHHMM
                file_date_str = txn_datetime.strftime("%y%m%d%H%M")
                filename = f"{acc_num}-{txn_id}-{file_date_str}"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                # 4. Generate the dummy content
                name, email = random.choice(DUMMY_NAMES)
                status = random.choice(["CREDITED", "DEBITED"])
                amount = f"{random.uniform(100.00, 5000.00):.2f}"
                date_string = txn_datetime.strftime("%H:%M %d %b %Y").upper()
                
                # Create the 16 pipe-separated fields
                # Matching the exact structure we saw in your file_reader.py
                fields = [
                    status,                  # [0] Status
                    email,                  # [1] Email
                    name,                   # [2] Name
                    acc_num,                # [3] Account No (Placeholder)
                    "",                     # [4] Remarks 1
                    amount,                 # [5] Amount
                    "",                     # [6] Fee
                    date_string,            # [7] Date String
                    "TEST THAP CR",         # [8] Description
                    "PANKAJKG",             # [9] Remarks 2
                    txn_id,                 # [10] Transaction ID (Placeholder)
                    "",                     # [11] Debit Account
                    "",                     # [12] Credit Account
                    "",                     # [13] Details 1
                    "",                     # [14] Details 2
                    ""                      # [15] Details 3
                ]
                
                content = "|".join(fields)
                
                # 5. Write the file
                with open(filepath, "w") as f:
                    f.write(content)
                    
    print("Success! Generated 1,000 transaction files.")

if __name__ == "__main__":
    generate_files()