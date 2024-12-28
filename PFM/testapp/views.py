from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Sum, F
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction,Budget
from .forms import TransactionForm
from .forms import ReportFilterForm
from .forms import BudgetForm
from django.core.serializers import serialize
import json
from django.http import JsonResponse, HttpResponse




def home(request):
    return render(request,'home.html')

def registerUser(request):


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        # context={'username':username, 'password':password, 'confirm_password':confirm_password}
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request,"Username already exists!")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, "Registration successful. Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match!")


    return render(request, 'register.html')


def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transction.html', {'transactions': transactions})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, "Transaction added successfully.")
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'add_transctions.html', {'form': form})

@login_required
def edit_transaction(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'edit_transction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect('transaction_list')
    return render(request, 'delete_transction.html', {'transaction': transaction})
@login_required(login_url='login')
def income_report(request):
    """View to display income report."""
    transactions = Transaction.objects.filter(user=request.user, transaction_type='income')
    total_income = transactions.aggregate(total=Sum('amount'))['total'] or 0
    form = ReportFilterForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date and end_date:
            transactions = Transaction.objects.filter(user=request.user, transaction_type='Income')
            total_income = transactions.aggregate(total=Sum('amount'))['total'] or 0


    categories = transactions.values('category').annotate(total=Sum('amount'))

    return render(request, 'income_report.html', {
        'transactions': transactions,
        'total_income': total_income,
        'categories': categories,
        'form': form,
    })


@login_required(login_url='login')
def expense_report(request):
    """View to display expense report."""
    transactions = Transaction.objects.filter(user=request.user, transaction_type='expense')
    total_expense = transactions.aggregate(total=Sum('amount'))['total'] or 0
    form = ReportFilterForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date and end_date:
            transactions = transactions.filter(date__range=[start_date, end_date])
            total_expense = transactions.aggregate(total=Sum('amount'))['total'] or 0


    categories = transactions.values('category').annotate(total=Sum('amount'))

    return render(request, 'expense_report.html', {
        'transactions': transactions,
        'total_expense': total_expense,
        'categories': categories,
        'form': form,
    })


@login_required(login_url='login')
def overview_report(request):
    # Get all transactions for the logged-in user
    incomes = Transaction.objects.filter(user=request.user, transaction_type='income')
    expenses = Transaction.objects.filter(user=request.user, transaction_type='expense')


    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense

    form = ReportFilterForm(request.GET)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date and end_date:
            incomes = incomes.filter(date__range=[start_date, end_date])
            expenses = expenses.filter(date__range=[start_date, end_date])
            # Recalculate totals for the filtered period
            total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
            total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
            net_balance = total_income - total_expense

    return render(request, 'overview_report.html', {
        'form': form,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    })



@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budget_list.html', {'budgets': budgets})


@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget added successfully.")
            return redirect('budget_list')
    else:
        form = BudgetForm()
    return render(request, 'add_budget.html', {'form': form})


@login_required
def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully.")
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'edit_budget.html', {'form': form})



@login_required
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget deleted successfully.")
        return redirect('budget_list')
    return render(request, 'delete_budget.html', {'budget': budget})


@login_required
def budget_exceedance(request):
    budgets = Budget.objects.filter(user=request.user)  # Filter by logged-in user
    exceeded_budgets = []

    for budget in budgets:
        # Calculate actual expenses for the category
        actual_expense = Transaction.objects.filter(
            user=request.user, category=budget.category
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Check if expenses exceed the budget limit
        if actual_expense > budget.budget_limit:
            exceeded_budgets.append({
                'category': budget.category,
                'set_budget': budget.budget_limit,
                'actual_expense': actual_expense,
                'difference': actual_expense - budget.budget_limit,
            })

    return render(request, 'budget_exceded.html', {'exceeded_budgets': exceeded_budgets})




@login_required
def set_budget(request):
    budgets = Budget.objects.filter(user=request.user).order_by('year', 'month', 'category')  # Show budgets sorted

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user

            # Check if a budget for the same category, month, and year exists
            existing_budget = Budget.objects.filter(
                user=request.user,
                category=budget.category,
                month=budget.month,
                year=budget.year
            ).first()

            if existing_budget:
                # Update the existing budget
                existing_budget.budget_limit = budget.budget_limit
                existing_budget.save()
                messages.success(request, "Existing budget updated successfully!")
            else:
                # Create a new budget
                budget.save()
                messages.success(request, "Budget set successfully!")
            return redirect('set_budget')

    else:
        form = BudgetForm()

    return render(request, 'set_budget.html', {'form': form, 'budgets': budgets})


def backup_data(request):
    transactions = Transaction.objects.all()
    data = serialize('json', transactions)

    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="transactions_backup.json"'

    return response




@login_required
def restore_data(request):
    if request.method == 'POST' and request.FILES['backup_file']:
        action = request.POST.get('action')  # "overwrite" or "merge"
        backup_file = request.FILES['backup_file']
        data = json.load(backup_file)

        current_user = request.user  # Get the logged-in user

        if action == "overwrite":
            # Overwrite: Clear all existing data for the current user
            Transaction.objects.filter(user=current_user).delete()

        elif action == "merge":
            # Merge: Avoid duplicates for the current user
            existing_transactions = Transaction.objects.filter(user=current_user).values_list(
                'transaction_type', 'category', 'amount', 'date'
            )
            for transaction_data in data:
                transaction = transaction_data['fields']
                transaction_tuple = (
                    transaction['transaction_type'],
                    transaction['category'],
                    transaction['amount'],
                    transaction['date']
                )
                if transaction_tuple not in existing_transactions:
                    Transaction.objects.create(
                        user=current_user,  # Associate with the logged-in user
                        transaction_type=transaction['transaction_type'],
                        category=transaction['category'],
                        amount=transaction['amount'],
                        date=transaction['date']
                    )

        return JsonResponse({"message": f"Data restored successfully with action: {action}"}, status=200)

    return render(request, 'restore.html')
