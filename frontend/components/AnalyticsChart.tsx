---
filename: components/AnalyticsChart.tsx
---
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface AnalyticsData {
  sessions: Array<{
    date: string;
    total_amount: number;
    success_count: number;
    failed_count: number;
  }>;
}

export function AnalyticsChart({ data }: { data: AnalyticsData }) {
  const chartData = (data?.sessions || []).map((s) => ({
    date: s.date,
    total: s.total_amount,
    موفق: s.success_count,
    ناموفق: s.failed_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="total" fill="#0ea5e9" />
      </BarChart>
    </ResponsiveContainer>
  );
}
