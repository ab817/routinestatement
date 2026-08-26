from django.db import models


class Transaction(models.Model):
    """
    Stores the complete 18-field transaction record received from
    the transaction source file.

    File_Transaction_ID is used as the primary key because it uniquely
    identifies the transaction.
    """

    # 12 - File_Transaction_ID
    file_transaction_id = models.CharField(
        max_length=100,
        primary_key=True
    )

    # 1 - Status
    status = models.CharField(
        max_length=20
    )

    # 2 - Email
    email = models.EmailField(
        blank=True,
        null=True
    )

    # 3 - Details_1
    details_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 4 - Account_Name
    account_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 5 - Masked_Account
    masked_account = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # 6 - Details_2
    details_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 7 - Amount
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    # 8 - Fees
    fees = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    # 9 - Date_Time
    date_time = models.DateTimeField()

    # 10 - Details_3
    details_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 11 - User
    user = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # 13 - Account_Number_1
    account_number_1 = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # 14 - Account_Number_2
    account_number_2 = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # 15 - Channel_Type
    channel_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # 16 - ID
    id_value = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # 17 - Payment_Details_2
    payment_details_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # 18 - Customer_Details
    customer_details = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # Internal system metadata
    imported_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.file_transaction_id} - {self.account_number_2}"