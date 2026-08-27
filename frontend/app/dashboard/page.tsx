import { MerchantSelector } from '@/components/MerchantSelector';
import { AnalyticsChart } from '@/components/AnalyticsChart';
import { DataTable } from '@/components/DataTable';

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  // Fetch merchants with null-safety
  const merchantsRes = await fetch('/api/merchants');
  const merchants = merchantsRes.ok ? await merchantsRes.json() : { merchants: [] };
  
  // Fetch analytics overview
  const overviewRes = await fetch('/api/analytics/overview');
  const overview = overviewRes.ok ? await overviewRes.json() : null;
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">داشبورد تحلیلی</h1>
      <MerchantSelector merchants={(merchants?.merchants || [])} />
      {overview && <AnalyticsChart data={overview} />}
      <DataTable />
    </div>
  );
}