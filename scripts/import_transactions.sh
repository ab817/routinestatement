#!/bin/bash

PROJECT_DIR="/path/to/routinestatement"
VENV_DIR="$PROJECT_DIR/.venv"

LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/transaction_import.log"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR" || exit 1

source "$VENV_DIR/bin/activate"

echo "============================================================" >> "$LOG_FILE"
echo "Transaction import started: $(date)" >> "$LOG_FILE"

python manage.py import_transactions >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "Transaction import finished: $(date)" >> "$LOG_FILE"
echo "Exit code: $EXIT_CODE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE