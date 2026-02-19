import { useCallback, useEffect, useState } from "react";
import api from "../api/client";

export function useDashboardData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const [summary, insights, charts] = await Promise.all([
      api.get("/dashboard/summary/"),
      api.get("/analytics/insights/"),
      api.get("/analytics/charts/"),
    ]);

    setData({ summary: summary.data, insights: insights.data, charts: charts.data });
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, refresh };
}
