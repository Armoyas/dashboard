'use client';

import { useState, useEffect } from 'react';
import MerchantSelector from '@/components/MerchantSelector';
import { AnalyticsChart } from '@/components/AnalyticsChart';
import { DataTable } from '@/components/DataTable';

export default function DashboardPage() {
  const [merchants, setMerchants] = useState<any>({ merchants: [] });
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    // Fetch merchants (client-side, after page load)
    fetch('/api/merchants')
      .then(res => res.ok ? res.json() : { merchants: [] })
      .then(data => setMerchants(data))
      .catch(() => setMerchants({ merchants: [] }));

    // Fetch analytics overview
    fetch('/api/analytics/overview')
      .then(res => res.ok ? res.json() : null)
      .then(data => setOverview(data))
      .catch(() => setOverview(null));
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">داشبورد تحلیلی</h1>
      <MerchantSelector merchants={(merchants?.merchants || [])} />
      {overview && <AnalyticsChart data={overview} />}
      <DataTable />
    </div>
  );
}