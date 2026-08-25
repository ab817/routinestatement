from django.db import models

class Transaction(models.Model):
    # The DC... ID is unique. We make it the primary key to prevent duplicates.
    transaction_id = models.CharField(max_length=50, primary_key=True)
    account_number = models.CharField(max_length=20)
    transaction_type = models.CharField(max_length=10) # CREDITED or DEBITED
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField()
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    description = models.CharField(max_length=200, blank=True, null=True)
    operator = models.CharField(max_length=50, blank=True, null=True)
    imported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.account_number}"