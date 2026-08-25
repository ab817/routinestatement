from rest_framework import serializers
from statements.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    # We want the date to be formatted nicely in the JSON response
    transaction_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = Transaction
        fields = '__all__' # This automatically includes all fields from the DB