from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from statements.models import Transaction
from .serializers import TransactionSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_api(request):
    # 1. Get parameters from the URL
    account_number = request.GET.get("account_number")
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    if not account_number or not from_date_str or not to_date_str:
        return Response(
            {"error": "account_number, from_date and to_date are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Parse the dates to ensure they are valid
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "Dates must be in YYYY-MM-DD format"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Query the Database! 
    # We filter by account number, and check if the transaction date falls between the two dates.
    transactions = Transaction.objects.filter(
        account_number=account_number,
        transaction_date__date__gte=from_date, # greater than or equal to
        transaction_date__date__lte=to_date    # less than or equal to
    ).order_by('transaction_date') # Sort chronologically

    # 3. Serialize the database records into JSON
    serializer = TransactionSerializer(transactions, many=True)

    return Response(serializer.data)