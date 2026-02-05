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

        if user and not user.is_staff:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'statements/login.html', {
            'error': 'Invalid credentials'
        })

    return render(request, 'statements/login.html')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')
    return render(request, 'statements/dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')


def download_statement(request):
    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)

    account_number = request.POST.get("account_number")
    from_date = request.POST.get("from_date")
    to_date = request.POST.get("to_date")

    if not account_number: 
        return HttpResponse("Account number missing", status=400)
    if not from_date:
        return HttpResponse("From date missing", status=400)
    if not to_date:
        return HttpResponse("To date missing", status=400)

    # convert dates
    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    timestamp = datetime.now().strftime("%Y%m%d")

    transactions = read_transactions(account_number, from_date, to_date)

    if not transactions:
        return render(request, "statements/dashboard.html", {
            "backend_error": "No transactions found"
        })

    csv_data = generate_csv(transactions)

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{account_number}_statement_{timestamp}.csv"'
    )

    return response

