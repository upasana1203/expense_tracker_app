from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from finance.models import Category, Transaction, SavingGoal, SavingContribution, Budget


class Command(BaseCommand):
    help = "Seed demo data for Smart Expense Tracker"

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email="demo@example.com",
            defaults={"username": "demo_user", "first_name": "Demo", "last_name": "User"},
        )
        user.set_password("DemoPass123!")
        user.save()

        categories = {
            "Salary": "income",
            "Investment": "income",
            "Food": "expense",
            "Travel": "expense",
            "Bills": "expense",
            "Shopping": "expense",
            "Emergency Fund": "saving",
        }

        cat_map = {}
        for name, ctype in categories.items():
            cat, _ = Category.objects.get_or_create(user=user, name=name, category_type=ctype, defaults={"is_default": False})
            cat_map[name] = cat

        today = date.today()
        sample_transactions = [
            (Decimal("4500.00"), "income", "Salary", today - timedelta(days=20), "Monthly salary"),
            (Decimal("400.00"), "income", "Investment", today - timedelta(days=18), "Dividends"),
            (Decimal("300.00"), "expense", "Food", today - timedelta(days=16), "Groceries"),
            (Decimal("220.00"), "expense", "Travel", today - timedelta(days=12), "Fuel and commute"),
            (Decimal("500.00"), "expense", "Bills", today - timedelta(days=10), "Utilities"),
            (Decimal("180.00"), "expense", "Shopping", today - timedelta(days=8), "Online order"),
            (Decimal("650.00"), "saving", "Emergency Fund", today - timedelta(days=5), "Savings transfer"),
        ]

        for amount, tx_type, cat_name, tx_date, note in sample_transactions:
            Transaction.objects.get_or_create(
                user=user,
                amount=amount,
                transaction_type=tx_type,
                category=cat_map[cat_name],
                date=tx_date,
                note=note,
            )

        goal, _ = SavingGoal.objects.get_or_create(
            user=user,
            name="Laptop",
            defaults={"target_amount": Decimal("50000.00"), "deadline": today + timedelta(days=180)},
        )
        SavingContribution.objects.get_or_create(user=user, goal=goal, amount=Decimal("15000.00"), date=today - timedelta(days=2), note="Initial contribution")
        Budget.objects.get_or_create(user=user, month=today.replace(day=1), defaults={"amount": Decimal("1500.00")})

        self.stdout.write(self.style.SUCCESS("Demo data seeded. Login: demo@example.com / DemoPass123!"))
