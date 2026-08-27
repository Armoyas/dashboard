import { useState } from 'react';

interface Merchant {
  merchant_key: string;
  name: string;
}

interface MerchantSelectorProps {
  merchants: Merchant[];
}

export function MerchantSelector({ merchants }: MerchantSelectorProps) {
  const [selectedMerchant, setSelectedMerchant] = useState<string>('');
  
  return (
    <div className="mb-4">
      <select
        value={selectedMerchant}
        onChange={(e) => setSelectedMerchant(e.target.value)}
        className="border rounded px-3 py-2 w-full"
      >
        <option value="">انتخاب فروشگاه</option>
        {(merchants || []).map((merchant) => (
          <option key={merchant.merchant_key} value={merchant.merchant_key}>
            {merchant.name}
          </option>
        ))}
      </select>
    </div>
  );
}