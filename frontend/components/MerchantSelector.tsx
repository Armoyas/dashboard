'use client';

import { useState, useEffect } from 'react';
import { getMerchants } from '@/lib/api';

interface Merchant {
  id: string;
  name: string;
  merchant_key: string;
}

export default function MerchantSelector({ 
  onSelect, 
  selectedMerchant 
}: { 
  onSelect: (merchant: Merchant | null) => void;
  selectedMerchant: Merchant | null;
}) {
  const [merchants, setMerchants] = useState<Merchant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchMerchants();
  }, []);

  const fetchMerchants = async () => {
    try {
      setLoading(true);
      const data = await getMerchants();
      setMerchants(data);
    } catch (error) {
      console.error('Failed to fetch merchants:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (merchant: Merchant) => {
    setSelected(merchant);
    setShowDropdown(false);
  };

  return (
    <div className="merchant-selector">
      <button 
        onClick={() => setShowDropdown(!showDropdown)}
        className="px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm"
      >
        {selectedMerchant ? selectedMerchant.name : 'Select Merchant'}
      </button>
      
      {showDropdown && (
        <div className="absolute mt-2 w-64 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
          {loading ? (
            <div className="p-4">Loading...</div>
          ) : (
            merchants.map(merchant => (
              <button
                key={merchant.id}
                onClick={() => handleSelect(merchant)}
                className="w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                {merchant.name}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}