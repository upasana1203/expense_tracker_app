import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function IncomeExpenseChart({ income = [], expense = [] }) {
  const months = Array.from(new Set([...income.map((i) => i.month), ...expense.map((e) => e.month)])).sort();
  const merged = months.map((month) => ({
    month,
    income: Number(income.find((i) => i.month === month)?.total || 0),
    expense: Number(expense.find((e) => e.month === month)?.total || 0),
  }));

  return (
    <div className="card chart-card">
      <h3>Income vs Expense</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={merged}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="income" fill="#0f766e" />
          <Bar dataKey="expense" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
