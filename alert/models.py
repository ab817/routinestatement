from django.db import models

class AlertMessage(models.Model):
    # Link to the transaction. If the transaction is deleted, delete the alert.
    transaction = models.ForeignKey('statements.Transaction', on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20) # SENT, FAILED, EXCLUDED
    sent_at = models.DateTimeField(auto_now_add=True)
    error_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction.transaction_id} - {self.status}"