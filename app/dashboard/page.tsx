"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { DollarSign, ArrowUpRight, Activity, Users } from "lucide-react";

interface Transaction {
  id: number;
  merchant_key: string;
  session_status: string;
  amount: number;
  adjusted_fee: number;
  created_at: string;
}

interface SummaryStats {
  total_transactions: number;
  total_volume: number;
  total_fees: number;
  active_merchants: number;
}

export default function DashboardPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<SummaryStats>({
    total_transactions: 0,
    total_volume: 0,
    total_fees: 0,
    active_merchants: 0,
  });
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
        const [txRes, statsRes] = await Promise.allSettled([
          axios.get(`${apiUrl}/api/transactions`),
          axios.get(`${apiUrl}/api/stats/summary`),
        ]);

        if (txRes.status === "fulfilled" && txRes.value.data) {
          const txData = txRes.value.data.transactions || txRes.value.data;
          setTransactions(Array.isArray(txData) ? txData : []);
        }

        if (statsRes.status === "fulfilled" && statsRes.value.data) {
          setStats(statsRes.value.data);
        }
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredTransactions = (transactions || []).filter((tx) => {
    if (statusFilter === "all") return true;
    return tx.session_status === statusFilter;
  });

  const chartData = [
    { name: "Completed", count: (transactions || []).filter((t) => t.session_status === "completed").length },
    { name: "Pending", count: (transactions || []).filter((t) => t.session_status === "pending").length },
    { name: "Failed", count: (transactions || []).filter((t) => t.session_status === "failed").length },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl font-semibold animate-pulse text-indigo-400">Loading Analytics...</div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header className="flex justify-between items-center border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">ZarrinPal Analytics Dashboard</h1>
          <p className="text-slate-400 mt-1">Transaction performance and merchant overview</p>
        </div>
        <span className="px-3 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Live System
        </span>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm font-medium">Total Volume</span>
            <DollarSign className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {stats.total_volume ? stats.total_volume.toLocaleString() : "0"} <span className="text-xs text-slate-400 font-normal">IRR</span>
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm font-medium">Total Transactions</span>
            <Activity className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {stats.total_transactions ? stats.total_transactions.toLocaleString() : transactions.length.toLocaleString()}
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm font-medium">Adjusted Fees</span>
            <ArrowUpRight className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {stats.total_fees ? stats.total_fees.toLocaleString() : "0"} <span className="text-xs text-slate-400 font-normal">IRR</span>
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-5 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm font-medium">Active Merchants</span>
            <Users className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold mt-2 text-white">
            {stats.active_merchants || 1}
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4 text-white">Transaction Status Breakdown</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155" }} />
              <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-white">Recent Transactions</h2>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="all">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs uppercase bg-slate-900/50 text-slate-400">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Merchant Key</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Amount (IRR)</th>
                <th className="px-4 py-3">Adjusted Fee</th>
                <th className="px-4 py-3">Created At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {filteredTransactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs">{tx.id}</td>
                  <td className="px-4 py-3 font-mono text-xs text-indigo-300">{tx.merchant_key}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        tx.session_status === "completed"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : tx.session_status === "pending"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}
                    >
                      {tx.session_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-white">{tx.amount.toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-400">{tx.adjusted_fee.toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{new Date(tx.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
