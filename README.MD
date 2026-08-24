Routine Statement & Transaction Alert System

A Django-based backend system designed to process bank transaction data from flat files, store it securely in a database, generate transaction statements (CSV/JSON), and dispatch automated email alerts to customers.

Features

File-Based Ingestion: Automatically parses transaction files from the email_support/ directory into a structured SQLite database.

Duplicate Prevention: Uses database-level unique constraints (Transaction ID) to ensure no transaction is imported twice.

Automated Email Alerts: Sends "Credited/Debited" email notifications to customers when new transactions are detected.

Exclusion List: Easily configurable list of account numbers that should not receive alert emails.

Alert Tracking: Maintains a database record of all sent, failed, and excluded alerts to prevent duplicate email spamming.

REST API: A JWT-authenticated API endpoint to query transactions by account number and date range.

Automated Cleanup: A management command that safely deletes old transaction files after a configurable retention period (e.g., 2 days), only if they are successfully backed up in the database.

Secure Credentials: Uses python-dotenv to keep email passwords and sensitive data out of the source code.

Architecture & Workflow

The system operates using decoupled, database-driven management commands:

email_support/ (Input Source)
        |
        v
+-----------------------+
|  import_transactions  |
| (Parses files,       |
|  prevents duplicates)|
+-----------+-----------+
            |
            v
+-----------------------+
|   Transaction Table   |
| (Persistent source   |
|      of truth)        |
+-----------+-----------+
            |
            v
+-----------------------+
|      run_alerts       |
| (Checks DB for        |
| unalerted transactions)|
+-----------+-----------+
            |
            v
      Excluded account?
         /        \
       YES         NO
        |           |
      Skip      Check AlertMessage DB
                    |
              +-----+------+
              |            |
            Sent?        Failed?
              |            |
            Skip      Record Error
                           |
                           v
                         Email

Tech Stack

Framework: Django 4.2+

API: Django REST Framework (DRF)

Authentication: SimpleJWT (Access & Refresh Tokens)

Database: SQLite (Development) - Configurable for PostgreSQL/MySQL for production.

Environment Management: python-dotenv

Installation and Setup

1. Clone and Set Up Virtual Environment

git clone <repository-url>
cd routinestatement

python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

2. Install Dependencies

pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file in the root directory (next to manage.py) and add your email credentials:

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

Note: If using Gmail, you must generate an "App Password" in your Google Account settings.

4. Apply Database Migrations

python manage.py migrate

5. Create a Superuser (for Admin Access)

python manage.py createsuperuser

Usage & Management Commands

The core operations are handled via Django management commands. These are designed to be run manually during development, and scheduled via Cron (Linux) or Windows Task Scheduler in production.

1. Import Transactions

Scans the email_support/ folder, parses the text files, and inserts new records into the database.

python manage.py import_transactions

2. Run Alert Routine

Queries the database for transactions that have not been alerted yet, checks the exclusion list, and sends emails. Records the result (SENT, FAILED, EXCLUDED) in the AlertMessage table.

python manage.py run_alerts

3. Cleanup Old Files

Deletes physical text files from email_support/ that are older than TRANSACTION_FILE_RETENTION_DAYS (Default: 2 days).

Safety Feature: A file will ONLY be deleted if its transaction data has been successfully imported into the database.

python manage.py cleanup_files

API Documentation

The system exposes a REST API for programmatic access to transaction data.

1. Authentication — Obtain JWT Tokens

The API is protected by JWT authentication. Obtain an access and refresh token by sending a POST request with your Django user credentials to:

POST /api/token/

Request Body:

{
  "username": "your_username",
  "password": "your_password"
}

Response:

{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}

Important: Keep actual access and refresh tokens private. Do not commit them to GitHub.

2. Get Transactions

Fetch a list of transactions for a specific account within a date range.

GET /api/transactions/

Authentication in Postman:

Open the Authorization tab.

Select Bearer Token as the authorization type.

Paste the JWT access token obtained from /api/token/ into the Token field.

Send the request.

Equivalent HTTP header:

Authorization: Bearer <your_access_token>

Query Parameters:

Parameter

Type

Description

account_number

string

Account number (16 digits)

from_date

date

Start date in YYYY-MM-DD format

to_date

date

End date in YYYY-MM-DD format

Example Request:

GET /api/transactions/?account_number=0100200000008016&from_date=2025-08-20&to_date=2025-08-24

Configuration

Core configurations can be adjusted in core/settings.py:

# Account numbers in this list will NOT receive alert emails
EXCLUDED_ACCOUNTS = [
    "0100200000008016",
]

# Number of days to keep physical files in email_support/
TRANSACTION_FILE_RETENTION_DAYS = 2

Production Scheduling (Cron / Task Scheduler)

For a production environment, do not run the commands manually. Use the server's OS-level task scheduler.

Linux (Cron)

# Run import every 5 minutes
*/5 * * * * /path/to/venv/bin/python /path/to/project/manage.py import_transactions

# Run alerts every 5 minutes (offset by 1 minute)
*/5 * * * * sleep 60 && /path/to/venv/bin/python /path/to/project/manage.py run_alerts

# Cleanup old files at midnight
0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py cleanup_files

Windows (Task Scheduler)

Set up three separate tasks pointing to your python.exe and manage.py paths, with the respective arguments:

import_transactions

run_alerts

cleanup_files

Project Workflow Summary

Transaction Files
      |
      v
Import Transactions
      |
      v
Database
      |
      +--------------------+
      |                    |
      v                    v
Transaction API       Alert Routine
      |                    |
      v                    v
JSON Response        Email Notification

Security Notes

Store email credentials in .env, not directly in source code.

Add .env to .gitignore before pushing the project to GitHub.

Never commit JWT access/refresh tokens, passwords, API keys, or other secrets.

Use a production database such as PostgreSQL/MySQL when deploying the system in a production environment.