
from django.test import TestCase
from django.contrib.auth.models import User
from testapp.models import Budget, Transaction
from django.db.models import Sum

class TransactionTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        # Create a sample transaction
        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type='Income',
            category='Salary',
            amount=5000.00,
            date='2024-12-14'
        )

    def test_transaction_creation(self):
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(self.transaction.category, 'Salary')

    def test_transaction_deletion(self):
        self.transaction.delete()
        self.assertEqual(Transaction.objects.count(), 0)

    def test_report_generation(self):
        response = self.client.get('/income_report/')
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '5000')



from django.test import TestCase

class BudgetTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

        # Create a budget for testing
        self.budget = Budget.objects.create(
            user=self.user,
            category="Food",
            budget_limit=500.00, month=12, year=2024
        )

        # Add a transaction within the budget
        self.transaction = Transaction.objects.create(
            user=self.user,
            transaction_type="Expense",
            category="Food",
            amount=400.00,
            date="2024-12-14"
        )

    def test_budget_creation(self):
        self.assertEqual(Budget.objects.count(), 1)
        self.assertEqual(self.budget.budget_limit, 500.00)

    def test_budget_exceedance(self):
        Transaction.objects.create(
            user=self.user,
            transaction_type="expense",
            category="Food",
            amount=200.00,  # This causes total expense = 400 + 200 = 600 > 500
            date="2024-12-15"
        )

        # Fetch updated transactions for the category "Food"
        total_expense = Transaction.objects.filter(
            user=self.user,
            category__iexact="Food"
        ).aggregate(total=Sum("amount"))['total'] or 0
        self.assertGreater(total_expense, self.budget.budget_limit, "Expenses should exceed the budget")

    def test_budget_update(self):
        """Test that budgets can be updated."""
        self.budget.budget_limit = 700.00
        self.budget.save()
        updated_budget = Budget.objects.get(id=self.budget.id)
        self.assertEqual(updated_budget.budget_limit, 700.00)

    def test_budget_deletion(self):
        """Test that budgets can be deleted."""
        self.budget.delete()
        self.assertEqual(Budget.objects.count(), 0)
