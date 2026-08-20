from django.shortcuts import render

# Create your views here.
from datetime import datetime

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import TransactionSerializer
from statements.services.file_reader import read_transactions


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_api(request):

    account_number = request.GET.get("account_number")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if not account_number or not from_date or not to_date:
        return Response(
            {
                "error": "account_number, from_date and to_date are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from_date = datetime.strptime(
            from_date, "%Y-%m-%d"
        ).date()

        to_date = datetime.strptime(
            to_date, "%Y-%m-%d"
        ).date()

    except ValueError:
        return Response(
            {
                "error": "Dates must be in YYYY-MM-DD format"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    transactions = read_transactions(
        account_number,
        from_date,
        to_date
    )

    serializer = TransactionSerializer(
        transactions,
        many=True
    )

    return Response(serializer.data)