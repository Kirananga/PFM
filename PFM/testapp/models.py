# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.category}: ${self.amount}"



class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.IntegerField(default=1)
    year = models.IntegerField(default=2024)


    def __str__(self):
        return f"{self.category} - {self.budget_limit} for {self.month}/{self.year}"
