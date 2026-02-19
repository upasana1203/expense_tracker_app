import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import api from "../api/client";
import ProgressBar from "../components/ProgressBar";

export default function SavingsPage() {
  const [goals, setGoals] = useState([]);
  const [goalForm, setGoalForm] = useState({ name: "", target_amount: "", deadline: "" });
  const [contribForm, setContribForm] = useState({ goal: "", amount: "", date: new Date().toISOString().slice(0, 10), note: "" });

  const loadGoals = async () => {
    const { data } = await api.get("/saving-goals/");
    setGoals(data);
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const createGoal = async (e) => {
    e.preventDefault();
    await api.post("/saving-goals/", goalForm);
    toast.success("Goal created");
    setGoalForm({ name: "", target_amount: "", deadline: "" });
    loadGoals();
  };

  const addContribution = async (e) => {
    e.preventDefault();
    await api.post("/saving-contributions/", contribForm);
    toast.success("Contribution added");
    setContribForm({ goal: "", amount: "", date: new Date().toISOString().slice(0, 10), note: "" });
    loadGoals();
  };

  return (
    <section className="page-grid">
      <h2>Savings & Goals</h2>

      <form className="card form-grid" onSubmit={createGoal}>
        <h3>Create Saving Goal</h3>
        <input required placeholder="Goal name" value={goalForm.name} onChange={(e) => setGoalForm({ ...goalForm, name: e.target.value })} />
        <input required type="number" min="1" step="0.01" placeholder="Target amount" value={goalForm.target_amount} onChange={(e) => setGoalForm({ ...goalForm, target_amount: e.target.value })} />
        <input type="date" value={goalForm.deadline} onChange={(e) => setGoalForm({ ...goalForm, deadline: e.target.value })} />
        <button>Create Goal</button>
      </form>

      <form className="card form-grid" onSubmit={addContribution}>
        <h3>Add Contribution</h3>
        <select required value={contribForm.goal} onChange={(e) => setContribForm({ ...contribForm, goal: e.target.value })}>
          <option value="">Select Goal</option>
          {goals.map((goal) => <option key={goal.id} value={goal.id}>{goal.name}</option>)}
        </select>
        <input required type="number" min="1" step="0.01" placeholder="Amount" value={contribForm.amount} onChange={(e) => setContribForm({ ...contribForm, amount: e.target.value })} />
        <input required type="date" value={contribForm.date} onChange={(e) => setContribForm({ ...contribForm, date: e.target.value })} />
        <input placeholder="Note" value={contribForm.note} onChange={(e) => setContribForm({ ...contribForm, note: e.target.value })} />
        <button>Add Contribution</button>
      </form>

      <div className="two-col">
        {goals.map((goal) => (
          <div key={goal.id} className="card">
            <h3>{goal.name}</h3>
            <p>Target: {goal.target_amount}</p>
            <p>Saved: {goal.current_amount}</p>
            <p>Remaining: {goal.remaining_amount}</p>
            <ProgressBar value={goal.current_amount} max={goal.target_amount} label="Progress" />
          </div>
        ))}
      </div>
    </section>
  );
}
