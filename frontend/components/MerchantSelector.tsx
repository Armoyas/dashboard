'use client';

import { useState } from 'react';

interface Merchant {
  merchant_key: string;
  name: string;
  created_at: string;
}

interface MerchantSelectorProps {
  merchants: Merchant[];
}

export default function MerchantSelector({ merchants }: MerchantSelectorProps) {
  const [selectedMerchant, setSelectedMerchant] = useState<string>('');

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium mb-2" htmlFor="merchant-select">
        انتخاب فروشگاه
      </label>
      <select
        id="merchant-select"
        value={selectedMerchant}
        onChange={(e) => setSelectedMerchant(e.target.value)}
        className="w-full p-3 border rounded-lg bg-white"
      >
        <option value="">همه فروشگاه‌ها</option>
        {(merchants || []).map((merchant) => (
          <option key={merchant.merchant_key} value={merchant.merchant_key}>
            {merchant.name}
          </option>
        ))}
      </select>
    </div>
  );
}