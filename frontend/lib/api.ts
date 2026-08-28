const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getMerchants() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/merchants`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching merchants:', error);
    return [];
  }
}

export async function getTransactions(params?: Record<string, string>) {
  try {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    const response = await fetch(`${API_BASE_URL}/api/transactions?${queryString}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching transactions:', error);
    return [];
  }
}

export async function getStatsSummary() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats/summary`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching stats summary:', error);
    return null;
  }
}

export interface Merchant {
  id: string;
  name: string;
  merchant_key: string;
}

export interface Transaction {
  id: string;
  session_key: string;
  merchant_key: string;
  amount: number;
  adjusted_fee: number;
  session_status: string;
  psp_code: string;
  created_at: string;
  try_created_at: string;
  verified_at: string | null;
}