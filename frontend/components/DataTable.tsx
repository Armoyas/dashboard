'use client'
import React from 'react';

interface Session {
  id: string;
  merchant_key: string;
  session_status: string;
  amount: number;
  created_at: string;
}

export function DataTable() {
  const [sessions, setSessions] = React.useState<Session[]>([]);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/sessions?limit=50');
        if (response.ok) {
          const data = await response.json();
          setSessions((data?.sessions || []));
        }
      } catch (error) {
        console.error('Error fetching sessions:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="text-center py-4">در حال بارگذاری...</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse">
        <thead>
          <tr>
            <th className="border p-2 text-right">وضعیت</th>
            <th className="border p-2 text-right">مبلغ (ریال)</th>
            <th className="border p-2 text-right">کلید فروشگاه</th>
          </tr>
        </thead>
        <tbody>
          {(sessions || []).map((session) => (
            <tr key={session.id}>
              <td className="border p-2">{session.session_status}</td>
              <td className="border p-2">{session.amount}</td>
              <td className="border p-2">{session.merchant_key}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}