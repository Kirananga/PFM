
from django import forms
from .models import Transaction
from .models import Budget

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'amount', 'date', 'description']


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))



class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'budget_limit', 'month', 'year']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'budget_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget Limit'}),
        }
