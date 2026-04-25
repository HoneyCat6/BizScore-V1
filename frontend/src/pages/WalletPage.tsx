import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Send, ArrowDownLeft, Plus, ChevronRight } from 'lucide-react';
import api from '../lib/api';

import { Spinner } from '../components/Spinner';

export default function WalletPage() {
  const [topUpAmount, setTopUpAmount] = useState('');
  const [topUpLoading, setTopUpLoading] = useState(false);
  const [showTopUp, setShowTopUp] = useState(false);
  const [msg, setMsg] = useState('');

  const handleTopUp = async (e: FormEvent) => {
    e.preventDefault();
    if (!topUpAmount || parseFloat(topUpAmount) <= 0) return;
    setTopUpLoading(true);
    setMsg('');
    try {
      await api.post('/wallet/topup', { amount: parseFloat(topUpAmount) });
      setMsg('Top up successful!');
      setTopUpAmount('');
      setShowTopUp(false);
    } catch {
      setMsg('Top up failed.');
    } finally {
      setTopUpLoading(false);
    }
  };

  return (
    <div className="px-5 pt-6 pb-4">
      <h1 className="text-xl font-bold text-gray-900 mb-5">My Wallet</h1>

      {msg && (
        <div className="bg-green-50 text-success text-sm px-4 py-3 rounded-xl mb-4">{msg}</div>
      )}

      {/* Actions */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <Link
          to="/wallet/send"
          className="flex flex-col items-center gap-2 bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors"
        >
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
            <Send size={20} className="text-primary-500" />
          </div>
          <span className="text-xs font-medium text-gray-700">Send</span>
        </Link>
        <Link
          to="/wallet/receive"
          className="flex flex-col items-center gap-2 bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <ArrowDownLeft size={20} className="text-success" />
          </div>
          <span className="text-xs font-medium text-gray-700">Receive</span>
        </Link>
        <button
          onClick={() => setShowTopUp(!showTopUp)}
          className="flex flex-col items-center gap-2 bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors"
        >
          <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
            <Plus size={20} className="text-warning" />
          </div>
          <span className="text-xs font-medium text-gray-700">Top Up</span>
        </button>
      </div>

      {/* Top Up Form */}
      {showTopUp && (
        <form onSubmit={handleTopUp} className="bg-gray-50 rounded-xl p-4 mb-6 space-y-3">
          <h3 className="text-sm font-semibold text-gray-900">Top Up Wallet</h3>
          <p className="text-xs text-gray-500">Simulated top up for demo purposes</p>
          <input
            type="number"
            min="1"
            step="0.01"
            value={topUpAmount}
            onChange={(e) => setTopUpAmount(e.target.value)}
            placeholder="Enter amount (RM)"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
          />
          <div className="flex gap-2">
            {[50, 100, 500, 1000].map((amt) => (
              <button
                key={amt}
                type="button"
                onClick={() => setTopUpAmount(String(amt))}
                className="flex-1 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:border-primary-500 hover:text-primary-500 transition-colors"
              >
                RM{amt}
              </button>
            ))}
          </div>
          <button
            type="submit"
            disabled={topUpLoading}
            className="w-full bg-primary-500 text-white py-3 rounded-xl font-semibold hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {topUpLoading ? <Spinner /> : 'Top Up Now'}
          </button>
        </form>
      )}

      {/* Quick Links */}
      <Link
        to="/transactions"
        className="flex items-center justify-between bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors"
      >
        <span className="text-sm font-medium text-gray-700">View Transaction History</span>
        <ChevronRight size={18} className="text-gray-400" />
      </Link>
    </div>
  );
}
