from rest_framework import serializers


class TransactionSerializer(serializers.Serializer):
    Status = serializers.CharField()
    Email = serializers.CharField()
    Name = serializers.CharField()
    Account_Number = serializers.CharField(source="Account Number")
    Remarks_1 = serializers.CharField(source="Remarks 1", allow_blank=True)
    Amount = serializers.CharField()
    Fee = serializers.CharField()
    Date = serializers.CharField()
    Description = serializers.CharField(allow_blank=True)
    Remarks_2 = serializers.CharField(source="Remarks 2", allow_blank=True)
    Transaction_ID = serializers.CharField(source="Transaction ID")
    Debit_Account = serializers.CharField(source="Debit Account", allow_blank=True)
    Credit_Account = serializers.CharField(source="Credit Account", allow_blank=True)
    Details_1 = serializers.CharField(source="Details 1", allow_blank=True)
    Details_2 = serializers.CharField(source="Details 2", allow_blank=True)
    Details_3 = serializers.CharField(source="Details 3", allow_blank=True)