export default function SummaryCard({ title, value, subtitle }) {
  return (
    <div className="card summary-card">
      <p>{title}</p>
      <h3>{value}</h3>
      {subtitle && <small>{subtitle}</small>}
    </div>
  );
}
