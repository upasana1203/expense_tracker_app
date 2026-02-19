from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Sum


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"
        SAVING = "saving", "Saving"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CategoryType.choices)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "name", "category_type")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"
        SAVING = "saving", "Saving"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions")
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.transaction_type} {self.amount}"


class SavingGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saving_goals")
    name = models.CharField(max_length=150)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["deadline", "created_at"]

    @property
    def current_amount(self):
        total = self.contributions.aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0")

    @property
    def progress_percent(self):
        if self.target_amount <= 0:
            return Decimal("0")
        return min((self.current_amount / self.target_amount) * Decimal("100"), Decimal("100"))

    @property
    def remaining_amount(self):
        return max(self.target_amount - self.current_amount, Decimal("0"))

    def __str__(self):
        return f"{self.name} - {self.user.email}"


class SavingContribution(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saving_contributions")
    goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, related_name="contributions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "-id"]


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    month = models.DateField(help_text="Use first day of month")
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("user", "month")
        ordering = ["-month"]

    def __str__(self):
        return f"{self.user.email} - {self.month:%Y-%m}"
