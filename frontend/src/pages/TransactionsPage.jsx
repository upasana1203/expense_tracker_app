import { useEffect, useMemo, useState } from "react";
import { toast } from "react-toastify";
import api from "../api/client";

const initialForm = {
  amount: "",
  transaction_type: "expense",
  category: "",
  date: new Date().toISOString().slice(0, 10),
  note: "",
};

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [filters, setFilters] = useState({
    search: "",
    transaction_type: "",
    category: "",
    start_date: "",
    end_date: "",
    amount_min: "",
    amount_max: "",
  });

  const fetchCategories = async () => {
    const { data } = await api.get("/categories/");
    setCategories(data);
  };

  const fetchTransactions = async () => {
    const query = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => value && query.append(key, value));
    const { data } = await api.get(`/transactions/?${query.toString()}`);
    setTransactions(data);
  };

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/transactions/${editingId}/`, form);
        toast.success("Transaction updated");
      } else {
        await api.post("/transactions/", form);
        toast.success("Transaction added");
      }
      setForm(initialForm);
      setEditingId(null);
      fetchTransactions();
    } catch (error) {
      toast.error("Unable to save transaction");
    }
  };

  const createCategory = async () => {
    if (!newCategoryName.trim()) return;
    try {
      await api.post("/categories/", { name: newCategoryName.trim(), category_type: form.transaction_type });
      toast.success("Category created");
      setNewCategoryName("");
      fetchCategories();
    } catch {
      toast.error("Could not create category");
    }
  };

  const onEdit = (tx) => {
    setEditingId(tx.id);
    setForm({
      amount: tx.amount,
      transaction_type: tx.transaction_type,
      category: tx.category,
      date: tx.date,
      note: tx.note,
    });
  };

  const onDelete = async (id) => {
    await api.delete(`/transactions/${id}/`);
    toast.success("Transaction removed");
    fetchTransactions();
  };

  const filteredCategories = useMemo(
    () => categories.filter((c) => c.category_type === form.transaction_type),
    [categories, form.transaction_type]
  );

  return (
    <section className="page-grid">
      <h2>Transactions</h2>
      <form className="card form-grid" onSubmit={submit}>
        <select value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value, category: "" })}>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
          <option value="saving">Saving</option>
        </select>
        <input type="number" min="0" step="0.01" placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
        <select required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
          <option value="">Select category</option>
          {filteredCategories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
        </select>
        <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
        <input placeholder="Note" value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
        <button>{editingId ? "Update" : "Add"} transaction</button>
      </form>

      <div className="card form-grid">
        <h3>Create Custom Category ({form.transaction_type})</h3>
        <input placeholder="Category name" value={newCategoryName} onChange={(e) => setNewCategoryName(e.target.value)} />
        <button onClick={createCategory} type="button">Add category</button>
      </div>

      <div className="card form-grid">
        <input placeholder="Search note/category" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
        <select value={filters.transaction_type} onChange={(e) => setFilters({ ...filters, transaction_type: e.target.value })}>
          <option value="">All types</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
          <option value="saving">Saving</option>
        </select>
        <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
          <option value="">All categories</option>
          {categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
        </select>
        <input type="date" value={filters.start_date} onChange={(e) => setFilters({ ...filters, start_date: e.target.value })} />
        <input type="date" value={filters.end_date} onChange={(e) => setFilters({ ...filters, end_date: e.target.value })} />
        <input type="number" min="0" step="0.01" placeholder="Min amount" value={filters.amount_min} onChange={(e) => setFilters({ ...filters, amount_min: e.target.value })} />
        <input type="number" min="0" step="0.01" placeholder="Max amount" value={filters.amount_max} onChange={(e) => setFilters({ ...filters, amount_max: e.target.value })} />
      </div>

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>Date</th><th>Type</th><th>Amount</th><th>Category</th><th>Note</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr key={tx.id}>
                <td>{tx.date}</td>
                <td>{tx.transaction_type}</td>
                <td>{tx.amount}</td>
                <td>{tx.category_name}</td>
                <td>{tx.note}</td>
                <td>
                  <button onClick={() => onEdit(tx)}>Edit</button>
                  <button onClick={() => onDelete(tx.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
