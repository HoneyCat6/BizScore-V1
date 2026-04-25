import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Send, ArrowDownLeft, TrendingUp, Award } from 'lucide-react';
import api from '../lib/api';
import { useAuth } from '../lib/auth';
import { formatMYR } from '../lib/types';
import type { WalletBalance, Transaction, ScoreResult } from '../lib/types';
import { PageLoader } from '../components/Spinner';

export default function DashboardPage() {
  const { user } = useAuth();
  const [balance, setBalance] = useState<WalletBalance | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [score, setScore] = useState<ScoreResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [balRes, txRes, scoreRes] = await Promise.allSettled([
          api.get('/wallet/balance'),
          api.get('/transactions', { params: { limit: 5 } }),
          api.get('/score/latest'),
        ]);
        if (balRes.status === 'fulfilled') setBalance(balRes.value.data);
        if (txRes.status === 'fulfilled') setTransactions(txRes.value.data);
        if (scoreRes.status === 'fulfilled') setScore(scoreRes.value.data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <PageLoader />;

  const todaySales = transactions
    .filter((t) => t.direction === 'inflow')
    .reduce((s, t) => s + t.amount, 0);
  const todayExpenses = transactions
    .filter((t) => t.direction === 'outflow')
    .reduce((s, t) => s + t.amount, 0);

  return (
    <div className="px-5 pt-6 pb-4">
      {/* Header */}
      <div className="mb-6">
        <p className="text-sm text-gray-500">Welcome back,</p>
        <h1 className="text-xl font-bold text-gray-900">{user?.name}</h1>
        <p className="text-xs text-gray-400">{user?.business_name}</p>
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl p-5 text-white mb-5">
        <p className="text-sm text-primary-200 mb-1">Wallet Balance</p>
        <p className="text-3xl font-bold">{balance ? formatMYR(balance.balance) : 'RM 0.00'}</p>
        <div className="flex gap-3 mt-4">
          <Link
            to="/wallet/send"
            className="flex-1 bg-white/20 rounded-xl py-2.5 text-center text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-white/30 transition-colors"
          >
            <Send size={16} /> Send
          </Link>
          <Link
            to="/wallet/receive"
            className="flex-1 bg-white/20 rounded-xl py-2.5 text-center text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-white/30 transition-colors"
          >
            <ArrowDownLeft size={16} /> Receive
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-green-50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp size={16} className="text-success" />
            <span className="text-xs text-gray-500">Recent Sales</span>
          </div>
          <p className="text-lg font-bold text-success">{formatMYR(todaySales)}</p>
        </div>
        <div className="bg-orange-50 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-1">
            <Send size={16} className="text-warning" />
            <span className="text-xs text-gray-500">Recent Expenses</span>
          </div>
          <p className="text-lg font-bold text-warning">{formatMYR(todayExpenses)}</p>
        </div>
      </div>

      {/* Score Card */}
      <Link to="/score" className="block bg-primary-50 rounded-xl p-4 mb-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
              <Award size={20} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Business Score</p>
              <p className="text-xs text-gray-500">
                {score ? score.tier : 'Not yet calculated'}
              </p>
            </div>
          </div>
          <span className="text-2xl font-bold text-primary-500">
            {score ? score.total_score : '--'}
          </span>
        </div>
      </Link>

      {/* Recent Transactions */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-gray-900">Recent Transactions</h2>
          <Link to="/transactions" className="text-xs text-primary-500 font-medium">View all</Link>
        </div>
        {transactions.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">No transactions yet. Start using your wallet!</p>
        ) : (
          <div className="space-y-2">
            {transactions.map((txn) => (
              <div key={txn.txn_id} className="flex items-center justify-between py-2.5 border-b border-gray-100 last:border-0">
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
                      {txn.counterparty_name || txn.counterparty_phone || txn.description || txn.category.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-gray-400">{txn.txn_date}</p>
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
        )}
      </div>
    </div>
  );
}
