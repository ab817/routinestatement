import os
import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand

from statements.models import Transaction
from statements.services.file_utils import (
    parse_filename,
    parse_transaction_line,
    parse_amount,
    parse_transaction_datetime,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scans transaction files and imports all 18 fields into the database."

    def handle(self, *args, **kwargs):

        root = getattr(
            settings,
            "TRANSACTION_FILES_ROOT",
            "email_support"
        )

        if not os.path.exists(root):
            self.stderr.write(
                self.style.ERROR(
                    f"Directory does not exist: {root}"
                )
            )
            return

        if not os.path.isdir(root):
            self.stderr.write(
                self.style.ERROR(
                    f"Transaction path is not a directory: {root}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "\nStarting Transaction Import..."
            )
        )

        imported_count = 0
        skipped_count = 0
        error_count = 0
        encoding_fallback_count = 0

        for filename in os.listdir(root):

            filepath = os.path.join(root, filename)

            # Ignore directories
            if not os.path.isfile(filepath):
                continue

            try:
                # ---------------------------------------------------------
                # 1. Parse filename
                # ---------------------------------------------------------

                meta = parse_filename(filename)

                if not meta:
                    raise ValueError(
                        "Invalid filename format. "
                        "Expected ACCOUNT-TRANSACTIONID-YYMMDDHHMM.txt"
                    )

                filename_account = meta["account_no"]
                filename_transaction_id = meta["transaction_id"]

                # ---------------------------------------------------------
                # 2. Read transaction file
                #
                # Primary encoding: UTF-8
                # Fallback encoding: CP1252
                # ---------------------------------------------------------

                try:
                    with open(
                        filepath,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        line = f.readline().strip()

                except UnicodeDecodeError:

                    encoding_fallback_count += 1

                    logger.warning(
                        "UTF-8 decoding failed for %s. "
                        "Retrying with CP1252.",
                        filename
                    )

                    self.stderr.write(
                        self.style.WARNING(
                            f"UTF-8 decoding failed for {filename}. "
                            f"Using CP1252 fallback."
                        )
                    )

                    try:
                        with open(
                            filepath,
                            "r",
                            encoding="cp1252"
                        ) as f:

                            line = f.readline().strip()

                    except UnicodeDecodeError as exc:

                        raise ValueError(
                            "Unable to decode transaction file "
                            "using UTF-8 or CP1252."
                        ) from exc

                if not line:
                    raise ValueError(
                        "Transaction file is empty."
                    )

                # ---------------------------------------------------------
                # 3. Parse all 18 fields
                # ---------------------------------------------------------

                data = parse_transaction_line(line)

                # ---------------------------------------------------------
                # 4. Validate File_Transaction_ID
                # ---------------------------------------------------------

                file_transaction_id = data["file_transaction_id"]

                if not file_transaction_id:
                    # Fall back to filename transaction ID
                    file_transaction_id = filename_transaction_id

                # If both IDs exist, make sure they agree.
                if (
                    data["file_transaction_id"]
                    and filename_transaction_id
                    and data["file_transaction_id"]
                    != filename_transaction_id
                ):
                    raise ValueError(
                        "Transaction ID mismatch: "
                        f"filename={filename_transaction_id}, "
                        f"content={data['file_transaction_id']}"
                    )

                # ---------------------------------------------------------
                # 5. Parse amount
                # ---------------------------------------------------------

                amount_value = parse_amount(
                    data["amount"]
                )

                try:
                    amount = Decimal(amount_value)

                except InvalidOperation as exc:

                    raise ValueError(
                        f"Invalid amount: {data['amount']}"
                    ) from exc

                # ---------------------------------------------------------
                # 6. Parse fees
                # ---------------------------------------------------------

                fees_value = parse_amount(
                    data["fees"]
                )

                try:
                    fees = Decimal(fees_value)

                except InvalidOperation as exc:

                    raise ValueError(
                        f"Invalid fees: {data['fees']}"
                    ) from exc

                # ---------------------------------------------------------
                # 7. Parse transaction date/time
                # ---------------------------------------------------------

                transaction_datetime = parse_transaction_datetime(
                    data["date_time"]
                )

                # ---------------------------------------------------------
                # 8. Import ALL 18 fields
                # ---------------------------------------------------------

                obj, created = Transaction.objects.get_or_create(
                    file_transaction_id=file_transaction_id,
                    defaults={
                        "status": data["status"],
                        "email": data["email"] or None,
                        "details_1": data["details_1"] or None,
                        "account_name": data["account_name"] or None,
                        "masked_account": data["masked_account"] or None,
                        "details_2": data["details_2"] or None,
                        "amount": amount,
                        "fees": fees,
                        "date_time": transaction_datetime,
                        "details_3": data["details_3"] or None,
                        "user": data["user"] or None,
                        "account_number_1": (
                            data["account_number_1"] or None
                        ),
                        "account_number_2": (
                            data["account_number_2"] or None
                        ),
                        "channel_type": (
                            data["channel_type"] or None
                        ),
                        "id_value": data["id_value"] or None,
                        "payment_details_2": (
                            data["payment_details_2"] or None
                        ),
                        "customer_details": (
                            data["customer_details"] or None
                        ),
                    },
                )

                # ---------------------------------------------------------
                # 9. Transaction already exists
                # ---------------------------------------------------------

                if created:

                    imported_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Imported: {file_transaction_id}"
                        )
                    )

                else:

                    skipped_count += 1

                    self.stdout.write(
                        f"Skipped (already in DB): "
                        f"{file_transaction_id}"
                    )

                # ---------------------------------------------------------
                # 10. Delete source file
                #
                # Safe because:
                # - newly created transaction is in DB
                # - existing transaction is already in DB
                # ---------------------------------------------------------

                try:

                    os.remove(filepath)

                    self.stdout.write(
                        f"  -> Deleted file: {filename}"
                    )

                except OSError as delete_error:

                    self.stderr.write(
                        self.style.WARNING(
                            f"  -> Database operation successful, "
                            f"but failed to delete file "
                            f"{filename}: {delete_error}"
                        )
                    )

            except Exception as exc:

                error_count += 1

                logger.exception(
                    "Error importing file %s",
                    filename
                )

                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to import {filename}: {exc}"
                    )
                )

        # -------------------------------------------------------------
        # Final summary
        # -------------------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "\nImport Complete."
            )
        )

        self.stdout.write(
            f"Imported             : {imported_count}"
        )

        self.stdout.write(
            f"Skipped              : {skipped_count}"
        )

        self.stdout.write(
            f"Encoding fallback    : {encoding_fallback_count}"
        )

        self.stdout.write(
            f"Errors               : {error_count}"
        )