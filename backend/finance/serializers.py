from decimal import Decimal
from rest_framework import serializers
from .models import Category, Transaction, SavingGoal, SavingContribution, Budget


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "category_type", "is_default")


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = ("id", "amount", "transaction_type", "category", "category_name", "date", "note", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at", "category_name")

    def validate(self, attrs):
        category = attrs.get("category")
        tx_type = attrs.get("transaction_type")
        request = self.context["request"]

        if category.user and category.user != request.user:
            raise serializers.ValidationError("Category does not belong to this user.")
        if category.category_type != tx_type:
            raise serializers.ValidationError("Category type must match transaction type.")
        if attrs.get("amount", Decimal("0")) <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return attrs


class SavingGoalSerializer(serializers.ModelSerializer):
    current_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_percent = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SavingGoal
        fields = (
            "id",
            "name",
            "target_amount",
            "deadline",
            "created_at",
            "current_amount",
            "progress_percent",
            "remaining_amount",
        )
        read_only_fields = ("created_at",)


class SavingContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingContribution
        fields = ("id", "goal", "amount", "date", "note")

    def validate(self, attrs):
        request = self.context["request"]
        goal = attrs.get("goal")
        if goal.user != request.user:
            raise serializers.ValidationError("Goal does not belong to this user.")
        if attrs.get("amount", Decimal("0")) <= 0:
            raise serializers.ValidationError("Contribution amount must be greater than zero.")
        return attrs


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ("id", "month", "amount")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value
