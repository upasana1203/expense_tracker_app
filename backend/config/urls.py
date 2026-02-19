from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import RegisterView, LogoutView
from finance.views import (
    CategoryViewSet,
    TransactionViewSet,
    SavingGoalViewSet,
    SavingContributionViewSet,
    BudgetViewSet,
    DashboardSummaryView,
    InsightView,
    ChartDataView,
    ExportCsvView,
    ExportExcelView,
    ExportPdfView,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"saving-goals", SavingGoalViewSet, basename="saving-goal")
router.register(r"saving-contributions", SavingContributionViewSet, basename="saving-contribution")
router.register(r"budgets", BudgetViewSet, basename="budget")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("api/analytics/insights/", InsightView.as_view(), name="insights"),
    path("api/analytics/charts/", ChartDataView.as_view(), name="charts"),
    path("api/reports/export/csv/", ExportCsvView.as_view(), name="export-csv"),
    path("api/reports/export/excel/", ExportExcelView.as_view(), name="export-excel"),
    path("api/reports/export/pdf/", ExportPdfView.as_view(), name="export-pdf"),
    path("api/", include(router.urls)),
]
