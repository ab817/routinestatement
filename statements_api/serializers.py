from rest_framework import serializers
from statements.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):

    Status = serializers.CharField(source="status")
    Account_Name = serializers.CharField(source="account_name")
    Amount = serializers.DecimalField(
        source="amount",
        max_digits=15,
        decimal_places=2
    )
    Fees = serializers.DecimalField(
        source="fees",
        max_digits=15,
        decimal_places=2
    )
    Date_Time = serializers.DateTimeField(
        source="date_time",
        format="%Y-%m-%d %H:%M:%S"
    )
    File_Transaction_ID = serializers.CharField(
        source="file_transaction_id"
    )
    Account_Number_1 = serializers.CharField(
        source="account_number_1"
    )
    Account_Number_2 = serializers.CharField(
        source="account_number_2"
    )
    Channel_Type = serializers.CharField(
        source="channel_type"
    )
    ID = serializers.CharField(
        source="id_value"
    )
    Payment_Details_2 = serializers.CharField(
        source="payment_details_2"
    )
    Customer_Details = serializers.CharField(
        source="customer_details"
    )

    class Meta:
        model = Transaction

        fields = [
            "Status",
            "Account_Name",
            "Amount",
            "Fees",
            "Date_Time",
            "File_Transaction_ID",
            "Account_Number_1",
            "Account_Number_2",
            "Channel_Type",
            "ID",
            "Payment_Details_2",
            "Customer_Details",
        ]

        read_only_fields = fields