import csv
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Transaction, SavingGoal, SavingContribution, Budget
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    SavingGoalSerializer,
    SavingContributionSerializer,
    BudgetSerializer,
)
from .services.analytics import (
    get_totals,
    get_monthly_overview,
    get_category_totals,
    get_trend_data,
    generate_insights,
    goal_trends,
)


DEFAULT_CATEGORIES = [
    ("Food", "expense"),
    ("Travel", "expense"),
    ("Bills", "expense"),
    ("Health", "expense"),
    ("Shopping", "expense"),
    ("Salary", "income"),
    ("Investment", "income"),
    ("Emergency Fund", "saving"),
    ("Retirement", "saving"),
]


def ensure_default_categories(user):
    for name, category_type in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            user=None,
            name=name,
            category_type=category_type,
            defaults={"is_default": True},
        )


class UserOwnedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(UserOwnedModelViewSet):
    serializer_class = CategorySerializer
    search_fields = ["name"]
    filterset_fields = ["category_type", "is_default"]

    def get_queryset(self):
        ensure_default_categories(self.request.user)
        return Category.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_default=False)


class TransactionViewSet(UserOwnedModelViewSet):
    serializer_class = TransactionSerializer
    filterset_fields = ["transaction_type", "category", "date"]
    search_fields = ["note", "category__name"]
    ordering_fields = ["amount", "date", "created_at"]

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        amount_min = self.request.query_params.get("amount_min")
        amount_max = self.request.query_params.get("amount_max")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if amount_min:
            queryset = queryset.filter(amount__gte=Decimal(amount_min))
        if amount_max:
            queryset = queryset.filter(amount__lte=Decimal(amount_max))

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingGoalViewSet(UserOwnedModelViewSet):
    serializer_class = SavingGoalSerializer
    search_fields = ["name"]

    def get_queryset(self):
        return SavingGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingContributionViewSet(UserOwnedModelViewSet):
    serializer_class = SavingContributionSerializer
    filterset_fields = ["goal", "date"]
    search_fields = ["note"]

    def get_queryset(self):
        return SavingContribution.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(UserOwnedModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        month = serializer.validated_data["month"].replace(day=1)
        serializer.save(user=self.request.user, month=month)

    def perform_update(self, serializer):
        month = serializer.validated_data.get("month", serializer.instance.month).replace(day=1)
        serializer.save(month=month)


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        total_summary = get_totals(request.user)
        monthly = get_monthly_overview(request.user, today)
        return Response({
            "summary": total_summary,
            "monthly_overview": monthly,
            "category_totals": {
                "income": get_category_totals(request.user, "income"),
                "expense": get_category_totals(request.user, "expense"),
                "saving": get_category_totals(request.user, "saving"),
            },
        })


class InsightView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(generate_insights(request.user, date.today()))


class ChartDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "expense_trend": get_trend_data(request.user, "expense"),
            "saving_trend": get_trend_data(request.user, "saving"),
            "income_vs_expense": {
                "income": get_trend_data(request.user, "income"),
                "expense": get_trend_data(request.user, "expense"),
            },
            "category_distribution": get_category_totals(request.user),
            "saving_growth": goal_trends(request.user),
        })


class ExportCsvView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(["Amount", "Type", "Category", "Date", "Note"])

        for tx in Transaction.objects.filter(user=request.user).select_related("category"):
            writer.writerow([tx.amount, tx.transaction_type, tx.category.name, tx.date, tx.note])
        return response


class ExportExcelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"
        ws.append(["Amount", "Type", "Category", "Date", "Note"])
        for tx in Transaction.objects.filter(user=request.user).select_related("category"):
            ws.append([float(tx.amount), tx.transaction_type, tx.category.name, tx.date.isoformat(), tx.note])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="transactions.xlsx"'
        return response


class ExportPdfView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, 760, "Smart Expense Tracker - Financial Summary")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, 742, f"Generated: {datetime.utcnow().isoformat()} UTC")

        summary = get_totals(request.user)
        y = 710
        for key, value in summary.items():
            pdf.drawString(40, y, f"{key.replace('_', ' ').title()}: {value}")
            y -= 18

        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, y, "Recent Transactions")
        pdf.setFont("Helvetica", 9)
        y -= 18
        for tx in Transaction.objects.filter(user=request.user).select_related("category")[:15]:
            line = f"{tx.date} | {tx.transaction_type} | {tx.category.name} | {tx.amount} | {tx.note[:40]}"
            pdf.drawString(40, y, line)
            y -= 14
            if y < 60:
                pdf.showPage()
                y = 760

        pdf.save()
        buffer.seek(0)
        return HttpResponse(buffer.getvalue(), content_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="financial_report.pdf"'})
