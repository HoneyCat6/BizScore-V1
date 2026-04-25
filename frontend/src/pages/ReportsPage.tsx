import { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, PieChart } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, PieChart as RPieChart, Pie, Tooltip } from 'recharts';
import api from '../lib/api';
import { formatMYR, formatCategory } from '../lib/types';
import type { PnLReport, CashFlowReport, CategoryBreakdown } from '../lib/types';
import { PageLoader } from '../components/Spinner';

const PIE_COLORS = ['#1a56db', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#ea580c', '#6b7280', '#db2777'];

export default function ReportsPage() {
  const [pnl, setPnl] = useState<PnLReport | null>(null);
  const [cashFlow, setCashFlow] = useState<CashFlowReport | null>(null);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('90d');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [pnlRes, cfRes, catRes] = await Promise.allSettled([
          api.get('/accounting/pnl', { params: { days: parseInt(period) } }),
          api.get('/accounting/cashflow', { params: { days: parseInt(period) } }),
          api.get('/accounting/categories', { params: { days: parseInt(period) } }),
        ]);
        if (pnlRes.status === 'fulfilled') setPnl(pnlRes.value.data);
        if (cfRes.status === 'fulfilled') setCashFlow(cfRes.value.data);
        if (catRes.status === 'fulfilled') setCategories(catRes.value.data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [period]);

  if (loading) return <PageLoader />;

  const pnlChart = pnl ? [
    { name: 'Revenue', value: pnl.revenue, color: '#059669' },
    { name: 'COGS', value: pnl.cost_of_goods, color: '#d97706' },
    { name: 'Gross Profit', value: pnl.gross_profit, color: '#1a56db' },
    { name: 'Op. Expenses', value: pnl.operating_expenses, color: '#dc2626' },
    { name: 'Net Profit', value: pnl.net_profit, color: pnl.net_profit >= 0 ? '#059669' : '#dc2626' },
  ] : [];

  const pieData = categories
    .filter((c) => c.total > 0)
    .map((c) => ({ name: formatCategory(c.category), value: c.total, percentage: c.percentage }));

  return (
    <div className="px-5 pt-6 pb-4">
      <h1 className="text-xl font-bold text-gray-900 mb-4">Financial Reports</h1>

      {/* Period Selector */}
      <div className="flex gap-2 mb-6">
        {[
          { v: '30', l: '30 Days' },
          { v: '90', l: '90 Days' },
          { v: '180', l: '6 Months' },
          { v: '365', l: '1 Year' },
        ].map(({ v, l }) => (
          <button
            key={v}
            onClick={() => setPeriod(v + 'd')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              period === v + 'd' ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {l}
          </button>
        ))}
      </div>

      {/* P&L Summary */}
      {pnl && (
        <div className="bg-white rounded-xl border border-gray-100 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 size={18} className="text-primary-500" />
            <h2 className="text-sm font-semibold text-gray-900">Profit & Loss</h2>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pnlChart} barSize={32}>
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(value) => formatMYR(Number(value))} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {pnlChart.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-3">
            <div className="bg-green-50 rounded-lg p-2.5">
              <p className="text-[10px] text-gray-500">Revenue</p>
              <p className="text-sm font-bold text-success">{formatMYR(pnl.revenue)}</p>
            </div>
            <div className={`${pnl.net_profit >= 0 ? 'bg-green-50' : 'bg-red-50'} rounded-lg p-2.5`}>
              <p className="text-[10px] text-gray-500">Net Profit</p>
              <p className={`text-sm font-bold ${pnl.net_profit >= 0 ? 'text-success' : 'text-danger'}`}>
                {formatMYR(pnl.net_profit)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Cash Flow */}
      {cashFlow && (
        <div className="bg-white rounded-xl border border-gray-100 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp size={18} className="text-primary-500" />
            <h2 className="text-sm font-semibold text-gray-900">Cash Flow</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Operating Inflow</span>
              <span className="text-sm font-semibold text-success">{formatMYR(cashFlow.operating_inflow)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Operating Outflow</span>
              <span className="text-sm font-semibold text-danger">{formatMYR(cashFlow.operating_outflow)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Capital Outflow</span>
              <span className="text-sm font-semibold text-warning">{formatMYR(cashFlow.capital_outflow)}</span>
            </div>
            <hr className="border-gray-100" />
            <div className="flex justify-between">
              <span className="text-sm font-semibold text-gray-900">Net Cash Flow</span>
              <span className={`text-sm font-bold ${cashFlow.net_cash_flow >= 0 ? 'text-success' : 'text-danger'}`}>
                {formatMYR(cashFlow.net_cash_flow)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Expense Breakdown */}
      {pieData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 p-4 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <PieChart size={18} className="text-primary-500" />
            <h2 className="text-sm font-semibold text-gray-900">Expense Breakdown</h2>
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RPieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                  labelLine={false}
                  fontSize={9}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatMYR(Number(value))} />
              </RPieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
