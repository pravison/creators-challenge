from django.db import models

# Create your models here.
from django.db import models

class STKPushTransaction(models.Model):
    """Store STK Push transaction details."""
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending, Successful, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount} KES - {self.status}"


class B2CPayment(models.Model):
    """Store B2C payment transaction details."""
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending, Successful, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.amount} KES - {self.status}"
