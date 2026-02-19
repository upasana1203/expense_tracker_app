import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = ["#0f766e", "#ea580c", "#0284c7", "#b45309", "#334155", "#64748b"];

export default function CategoryPieChart({ data }) {
  return (
    <div className="card chart-card">
      <h3>Category Distribution</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={data} dataKey="total" nameKey="category" outerRadius={90}>
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
