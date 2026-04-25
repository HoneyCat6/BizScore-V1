import { useEffect, useState } from 'react';
import { ArrowDownLeft, Send, Filter } from 'lucide-react';
import api from '../lib/api';
import { formatMYR, formatCategory } from '../lib/types';
import type { Transaction } from '../lib/types';
import { PageLoader } from '../components/Spinner';

export default function TransactionHistoryPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'inflow' | 'outflow'>('all');

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get('/transactions', { params: { limit: 100 } });
        setTransactions(data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <PageLoader />;

  const filtered = filter === 'all'
    ? transactions
    : transactions.filter((t) => t.direction === filter);

  const grouped = filtered.reduce<Record<string, Transaction[]>>((acc, txn) => {
    const date = txn.txn_date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(txn);
    return acc;
  }, {});

  return (
    <div className="px-5 pt-6 pb-4">
      <h1 className="text-xl font-bold text-gray-900 mb-4">Transactions</h1>

      {/* Filter */}
      <div className="flex items-center gap-2 mb-5">
        <Filter size={16} className="text-gray-400" />
        {(['all', 'inflow', 'outflow'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filter === f ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'all' ? 'All' : f === 'inflow' ? 'Income' : 'Expenses'}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-16">No transactions found</p>
      ) : (
        Object.entries(grouped).map(([date, txns]) => (
          <div key={date} className="mb-5">
            <p className="text-xs font-medium text-gray-400 mb-2">{date}</p>
            <div className="bg-white rounded-xl border border-gray-100 divide-y divide-gray-50">
              {txns.map((txn) => (
                <div key={txn.txn_id} className="flex items-center justify-between p-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      txn.direction === 'inflow' ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {txn.direction === 'inflow' ? (
                        <ArrowDownLeft size={14} className="text-success" />
                      ) : (
                        <Send size={14} className="text-danger" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {txn.counterparty_name || txn.description || formatCategory(txn.category)}
                      </p>
                      <p className="text-xs text-gray-400">{formatCategory(txn.category)}</p>
                    </div>
                  </div>
                  <span className={`text-sm font-semibold ${
                    txn.direction === 'inflow' ? 'text-success' : 'text-danger'
                  }`}>
                    {txn.direction === 'inflow' ? '+' : '-'}{formatMYR(txn.amount)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
