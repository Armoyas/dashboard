'use client';

import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface TransactionSummary {
  date: string;
  total_amount: number;
  total_transactions: number;
  success_rate: number;
}

export default function AnalyticsChart({ 
  data 
}: { 
  data: TransactionSummary[];
}) {
  const chartData = {
    labels: data.map(item => item.date),
    datasets: [
      {
        label: 'Total Amount (IRR)',
        data: data.map(item => item.total_amount),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 1,
      },
      {
        label: 'Transaction Count',
        data: data.map(item => item.total_transactions),
        backgroundColor: 'rgba(255, 159, 64, 0.6)',
        borderColor: 'rgb(255, 159, 64)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Transaction Analytics',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return <Bar data={chartData} options={options} />;
}