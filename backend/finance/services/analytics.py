from collections import defaultdict
from decimal import Decimal
from datetime import date
from calendar import monthrange
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from ..models import Transaction, Budget, SavingContribution


def first_day_of_month(value):
    return value.replace(day=1)


def month_range(value):
    start = first_day_of_month(value)
    end = value.replace(day=monthrange(value.year, value.month)[1])
    return start, end


def get_totals(user, start_date=None, end_date=None):
    qs = Transaction.objects.filter(user=user)
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    totals = qs.values("transaction_type").annotate(total=Sum("amount"))
    bucket = {"income": Decimal("0"), "expense": Decimal("0"), "saving": Decimal("0")}
    for row in totals:
        bucket[row["transaction_type"]] = row["total"] or Decimal("0")

    balance = bucket["income"] - bucket["expense"]
    net_savings = bucket["saving"] + (bucket["income"] - bucket["expense"])
    return {
        "total_income": bucket["income"],
        "total_expenses": bucket["expense"],
        "total_savings": bucket["saving"],
        "total_balance": balance,
        "net_savings": net_savings,
    }


def get_monthly_overview(user, reference_date):
    start, end = month_range(reference_date)
    totals = get_totals(user, start, end)
    totals["month"] = start.strftime("%Y-%m")
    return totals


def get_category_totals(user, tx_type=None):
    qs = Transaction.objects.filter(user=user)
    if tx_type:
        qs = qs.filter(transaction_type=tx_type)
    data = qs.values("category__name").annotate(total=Sum("amount")).order_by("-total")
    return [{"category": row["category__name"], "total": row["total"] or Decimal("0")} for row in data]


def get_trend_data(user, tx_type=None):
    qs = Transaction.objects.filter(user=user)
    if tx_type:
        qs = qs.filter(transaction_type=tx_type)
    monthly = (
        qs.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    return [{"month": row["month"].strftime("%Y-%m"), "total": row["total"] or Decimal("0")} for row in monthly]


def calculate_budget_status(user, reference_date):
    start = first_day_of_month(reference_date)
    budget = Budget.objects.filter(user=user, month=start).first()
    spent = (
        Transaction.objects.filter(user=user, transaction_type="expense", date__year=start.year, date__month=start.month)
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0")
    )
    if not budget:
        return {"budget": None, "spent": spent, "remaining": None, "percent_used": Decimal("0"), "alert": None}

    percent = (spent / budget.amount * Decimal("100")) if budget.amount > 0 else Decimal("0")
    remaining = budget.amount - spent
    alert = None
    if percent >= 100:
        alert = "Budget exceeded"
    elif percent >= 80:
        alert = "Budget at 80%"

    return {
        "budget": budget.amount,
        "spent": spent,
        "remaining": remaining,
        "percent_used": percent.quantize(Decimal("0.01")),
        "alert": alert,
    }


def monthly_comparison(user, reference_date):
    current_start = first_day_of_month(reference_date)
    prev_month = (current_start.replace(day=1) - date.resolution).replace(day=1)

    current_expense = (
        Transaction.objects.filter(user=user, transaction_type="expense", date__year=current_start.year, date__month=current_start.month)
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0")
    )
    previous_expense = (
        Transaction.objects.filter(user=user, transaction_type="expense", date__year=prev_month.year, date__month=prev_month.month)
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0")
    )

    if previous_expense == 0:
        change_pct = Decimal("0")
    else:
        change_pct = ((current_expense - previous_expense) / previous_expense * Decimal("100")).quantize(Decimal("0.01"))
    return current_expense, previous_expense, change_pct


def get_saving_recommendation(user, reference_date):
    monthly_income = (
        Transaction.objects.filter(user=user, transaction_type="income", date__year=reference_date.year, date__month=reference_date.month)
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0")
    )
    target_rate = Decimal("0.20")
    return (monthly_income * target_rate).quantize(Decimal("0.01"))


def generate_insights(user, reference_date):
    totals = get_monthly_overview(user, reference_date)
    category_totals = get_category_totals(user, "expense")
    top_category = category_totals[0] if category_totals else None
    current_expense, previous_expense, change_pct = monthly_comparison(user, reference_date)

    income = totals["total_income"]
    expense = totals["total_expenses"]
    saving = totals["total_savings"]
    saving_rate = (saving / income * Decimal("100")).quantize(Decimal("0.01")) if income > 0 else Decimal("0")
    income_expense_ratio = (income / expense).quantize(Decimal("0.01")) if expense > 0 else Decimal("0")

    insights = []
    if top_category:
        insights.append(f"Highest spending category: {top_category['category']}.")
    if change_pct > 0:
        insights.append(f"Your expenses increased by {change_pct}% compared to last month.")
    elif change_pct < 0:
        insights.append(f"Great work. Expenses dropped by {abs(change_pct)}% compared to last month.")

    if saving_rate >= 20:
        insights.append(f"You saved {saving_rate}% of your income. Good job.")
    elif income > 0:
        insights.append(f"You saved {saving_rate}% of income. Try targeting at least 20%.")

    budget_status = calculate_budget_status(user, reference_date)
    if budget_status["alert"]:
        insights.append(budget_status["alert"])

    spikes = detect_unusual_spikes(user, reference_date)
    insights.extend(spikes)

    return {
        "highest_spending_category": top_category,
        "monthly_expense_current": current_expense,
        "monthly_expense_previous": previous_expense,
        "expense_change_percent": change_pct,
        "saving_rate_percent": saving_rate,
        "income_expense_ratio": income_expense_ratio,
        "budget": budget_status,
        "recommended_monthly_saving": get_saving_recommendation(user, reference_date),
        "insight_messages": insights,
    }


def detect_unusual_spikes(user, reference_date):
    current_month = Transaction.objects.filter(
        user=user,
        transaction_type="expense",
        date__year=reference_date.year,
        date__month=reference_date.month,
    )
    previous_month = Transaction.objects.filter(
        user=user,
        transaction_type="expense",
        date__year=(reference_date.replace(day=1) - date.resolution).year,
        date__month=(reference_date.replace(day=1) - date.resolution).month,
    )

    prev_map = defaultdict(lambda: Decimal("0"))
    for row in previous_month.values("category__name").annotate(total=Sum("amount")):
        prev_map[row["category__name"]] = row["total"] or Decimal("0")

    messages = []
    for row in current_month.values("category__name").annotate(total=Sum("amount")):
        cat = row["category__name"]
        curr = row["total"] or Decimal("0")
        prev = prev_map[cat]
        if prev > 0 and curr > prev * Decimal("1.3"):
            increase = ((curr - prev) / prev * Decimal("100")).quantize(Decimal("0.01"))
            messages.append(f"Spending spike detected: {cat} is up by {increase}%.")

    return messages


def goal_trends(user):
    monthly = (
        SavingContribution.objects.filter(user=user)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    return [{"month": row["month"].strftime("%Y-%m"), "total": row["total"] or Decimal("0")} for row in monthly]
