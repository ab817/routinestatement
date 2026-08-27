from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .services.file_reader import read_transactions
from .services.csv_generator import generate_csv
import os
from datetime import datetime

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'statements/login.html', {
            'error': 'Invalid credentials'
        })

    return render(request, 'statements/login.html')


@login_required
@login_required
def dashboard(request):
    return render(request, "statements/dashboard.html")

def user_logout(request):
    logout(request)
    return redirect('user_login')

#download csv statement
def download_statement(request):

    if request.method != "POST":
        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": "Invalid request.",
            }
        )

    account_number = request.POST.get("account_number", "").strip()
    from_date_str = request.POST.get("from_date", "").strip()
    to_date_str = request.POST.get("to_date", "").strip()

    # ---------------------------------------------------------
    # Validate account number
    # ---------------------------------------------------------

    if not account_number:
        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": "Account number is required.",
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Validate From Date
    # ---------------------------------------------------------

    if not from_date_str:
        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": "From Date is required.",
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Validate To Date
    # ---------------------------------------------------------

    if not to_date_str:
        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": "To Date is required.",
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Convert dates
    # ---------------------------------------------------------

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

        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": "Invalid date format.",
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Validate date range
    # ---------------------------------------------------------

    if from_date > to_date:

        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": (
                    "From Date cannot be later than To Date."
                ),
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Read transactions
    # ---------------------------------------------------------

    transactions = read_transactions(
        account_number,
        from_date,
        to_date
    )

    # ---------------------------------------------------------
    # No transactions found
    # ---------------------------------------------------------

    if not transactions:

        return render(
            request,
            "statements/dashboard.html",
            {
                "backend_error": (
                    "No transactions found for the "
                    "given account and date range."
                ),
                "account_number": account_number,
                "from_date": from_date_str,
                "to_date": to_date_str,
            }
        )

    # ---------------------------------------------------------
    # Generate CSV
    # ---------------------------------------------------------

    csv_data = generate_csv(transactions)

    timestamp = datetime.now().strftime("%Y%m%d")

    response = HttpResponse(
        csv_data,
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        f'attachment; '
        f'filename="{account_number}_statement_{timestamp}.csv"'
    )

    return response

