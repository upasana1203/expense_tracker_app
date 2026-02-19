import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api/client";
import ProgressBar from "../components/ProgressBar";

export default function BudgetPage() {
  const [budgets, setBudgets] = useState([]);
  const [insights, setInsights] = useState(null);
  const [form, setForm] = useState({ month: new Date().toISOString().slice(0, 10), amount: "" });

  const load = async () => {
    const [budgetRes, insightRes] = await Promise.all([api.get("/budgets/"), api.get("/analytics/insights/")]);
    setBudgets(budgetRes.data);
    setInsights(insightRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  const saveBudget = async (e) => {
    e.preventDefault();
    try {
      await api.post("/budgets/", form);
      toast.success("Budget saved");
      setForm({ month: new Date().toISOString().slice(0, 10), amount: "" });
      load();
    } catch {
      toast.error("Could not save budget. If month exists, edit from API or add update UI flow.");
    }
  };

  const budget = insights?.budget;

  return (
    <section className="page-grid">
      <h2>Budget Planner</h2>
      <form className="card form-grid" onSubmit={saveBudget}>
        <input type="date" required value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} />
        <input type="number" required min="1" step="0.01" placeholder="Monthly budget" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
        <button>Set Budget</button>
      </form>

      <div className="card">
        <h3>Current Budget Status</h3>
        {budget?.budget ? (
          <>
            <p>Budget: {budget.budget}</p>
            <p>Spent: {budget.spent}</p>
            <p>Remaining: {budget.remaining}</p>
            <ProgressBar value={budget.spent} max={budget.budget} label="Usage" />
            {budget.alert && <p className="alert">{budget.alert}</p>}
          </>
        ) : (
          <p>No budget set for current month.</p>
        )}
      </div>

      <div className="card table-wrap">
        <table>
          <thead><tr><th>Month</th><th>Amount</th></tr></thead>
          <tbody>
            {budgets.map((b) => (
              <tr key={b.id}><td>{b.month}</td><td>{b.amount}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
