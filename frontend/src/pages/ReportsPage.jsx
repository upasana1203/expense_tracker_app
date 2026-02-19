import api from "../api/client";
import { toast } from "react-toastify";

async function download(path, filename) {
  try {
    const response = await api.get(path, { responseType: "blob" });
    const url = URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    toast.error("Download failed");
  }
}

export default function ReportsPage() {
  return (
    <section className="page-grid">
      <h2>Reports & Export</h2>
      <div className="card">
        <p>Export your records to CSV, Excel, or PDF summary report.</p>
        <div className="row-actions">
          <button onClick={() => download("/reports/export/csv/", "transactions.csv")}>Export CSV</button>
          <button onClick={() => download("/reports/export/excel/", "transactions.xlsx")}>Export Excel</button>
          <button onClick={() => download("/reports/export/pdf/", "financial_report.pdf")}>Export PDF</button>
        </div>
      </div>
    </section>
  );
}
