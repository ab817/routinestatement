from datetime import datetime

from django.db.models import Q

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework import status

from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from statements.models import Transaction
from .serializers import TransactionSerializer
from .permissions import (
    IsActiveAPIConsumer,
    IsAllowedIP,
)


@api_view(["GET"])
@authentication_classes([OAuth2Authentication])
@permission_classes([
    IsActiveAPIConsumer,
    IsAllowedIP,
])
def transaction_api(request):

    account_number = request.GET.get("account_number")
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    if not account_number or not from_date_str or not to_date_str:
        return Response(
            {
                "error": (
                    "account_number, from_date and "
                    "to_date are required"
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from_date = datetime.strptime(
            from_date_str,
            "%Y-%m-%d"
        ).date()

        to_date = datetime.strptime(
            to_date_str,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return Response(
            {
                "error": "Dates must be in YYYY-MM-DD format"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    transactions = Transaction.objects.filter(
        Q(account_number_1=account_number) |
        Q(account_number_2=account_number),
        date_time__date__gte=from_date,
        date_time__date__lte=to_date
    ).order_by(
        "date_time"
    )

    serializer = TransactionSerializer(
        transactions,
        many=True
    )

    return Response(serializer.data)