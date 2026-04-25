import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Send, Package, Settings, Users, Home, Zap, TrendingUp, ShoppingCart, CreditCard, MoreHorizontal } from 'lucide-react';
import api from '../lib/api';
import { OUTFLOW_CATEGORIES, formatMYR } from '../lib/types';
import { Spinner } from '../components/Spinner';

const iconMap: Record<string, React.ElementType> = {
  Package, Settings, Users, Home, Zap, TrendingUp, ShoppingCart, CreditCard, MoreHorizontal,
};

export default function SendPaymentPage() {
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!category) { setError('Please select a category'); return; }
    setError('');
    setLoading(true);
    try {
      await api.post('/wallet/send', {
        amount: parseFloat(amount),
        recipient_phone: recipientPhone,
        category,
        description,
      });
      setSuccess(true);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Payment failed.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="px-5 pt-6 pb-4 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mt-16 mb-4">
          <Send size={28} className="text-success" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Payment Sent!</h2>
        <p className="text-gray-500 mb-2">{formatMYR(parseFloat(amount))} to {recipientPhone}</p>
        <p className="text-sm text-gray-400 mb-8">
          Categorized as: {OUTFLOW_CATEGORIES.find((c) => c.value === category)?.label}
        </p>
        <button
          onClick={() => navigate('/wallet')}
          className="w-full bg-primary-500 text-white py-3 rounded-xl font-semibold"
        >
          Back to Wallet
        </button>
      </div>
    );
  }

  return (
    <div className="px-5 pt-6 pb-4">
      <button onClick={() => navigate(-1)} className="inline-flex items-center text-gray-500 text-sm mb-4">
        <ChevronLeft size={18} /> Back
      </button>
      <h1 className="text-xl font-bold text-gray-900 mb-5">Send Payment</h1>

      {error && <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-xl mb-4">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Amount (RM)</label>
          <input
            type="number"
            required
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none text-2xl font-bold text-center"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Recipient Phone</label>
          <input
            type="tel"
            required
            value={recipientPhone}
            onChange={(e) => setRecipientPhone(e.target.value)}
            placeholder="e.g. 60123456789"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">What is this payment for?</label>
          <div className="grid grid-cols-3 gap-2">
            {OUTFLOW_CATEGORIES.map((cat) => {
              const Icon = iconMap[cat.icon] || MoreHorizontal;
              const selected = category === cat.value;
              return (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setCategory(cat.value)}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all ${
                    selected
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-100 bg-gray-50 text-gray-600 hover:border-gray-200'
                  }`}
                >
                  <Icon size={20} />
                  <span className="text-[10px] font-medium leading-tight text-center">{cat.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Note (optional)</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Monthly rent payment"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-500 text-white py-4 rounded-xl font-semibold text-lg hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center gap-2 mt-4"
        >
          {loading ? <><Spinner /> Sending...</> : `Send ${amount ? formatMYR(parseFloat(amount)) : ''}`}
        </button>
      </form>
    </div>
  );
}
