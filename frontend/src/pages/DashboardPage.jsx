import { useMemo } from "react";
import SummaryCard from "../components/SummaryCard";
import TrendChart from "../components/charts/TrendChart";
import CategoryPieChart from "../components/charts/CategoryPieChart";
import IncomeExpenseChart from "../components/charts/IncomeExpenseChart";
import { useDashboardData } from "../hooks/useDashboardData";

export default function DashboardPage() {
  const { data, loading } = useDashboardData();

  const cards = useMemo(() => {
    if (!data) return [];
    const summary = data.summary.summary;
    return [
      ["Total Balance", summary.total_balance],
      ["Total Income", summary.total_income],
      ["Total Expenses", summary.total_expenses],
      ["Total Savings", summary.total_savings],
      ["Net Savings", summary.net_savings],
      ["Current Month", data.summary.monthly_overview.month],
    ];
  }, [data]);

  if (loading || !data) return <div className="card">Loading dashboard...</div>;

  return (
    <section className="page-grid">
      <header>
        <h2>Financial Overview</h2>
        <p>Auto-updated intelligence for spending and saving behavior.</p>
      </header>

      <div className="summary-grid">
        {cards.map(([title, value]) => (
          <SummaryCard key={title} title={title} value={value} />
        ))}
      </div>

      <div className="two-col">
        <TrendChart title="Monthly Expenses" data={data.charts.expense_trend} color="#dc2626" />
        <TrendChart title="Savings Growth" data={data.charts.saving_growth} color="#0f766e" />
      </div>

      <div className="two-col">
        <CategoryPieChart data={data.charts.category_distribution} />
        <IncomeExpenseChart income={data.charts.income_vs_expense.income} expense={data.charts.income_vs_expense.expense} />
      </div>

      <div className="card">
        <h3>Smart Insights</h3>
        <ul>
          {data.insights.insight_messages.map((msg) => (
            <li key={msg}>{msg}</li>
          ))}
        </ul>
        <p>Saving rate: {data.insights.saving_rate_percent}%</p>
        <p>Income/Expense ratio: {data.insights.income_expense_ratio}</p>
        <p>Recommended monthly saving: {data.insights.recommended_monthly_saving}</p>
      </div>
    </section>
  );
}
