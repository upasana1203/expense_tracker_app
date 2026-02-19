export default function ProgressBar({ value = 0, max = 100, label }) {
  const percent = Math.min((Number(value) / Number(max || 1)) * 100, 100);
  return (
    <div>
      {label && <p>{label}</p>}
      <div className="progress-wrap">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <small>{percent.toFixed(1)}%</small>
    </div>
  );
}
