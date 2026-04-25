import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, QrCode, ArrowDownLeft } from 'lucide-react';
import api from '../lib/api';
import { formatMYR } from '../lib/types';
import { Spinner } from '../components/Spinner';

export default function ReceivePaymentPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'qr' | 'manual'>('qr');
  const [qrUrl, setQrUrl] = useState<string | null>(null);
  const [loadingQr, setLoadingQr] = useState(false);

  // Manual receive
  const [amount, setAmount] = useState('');
  const [payerPhone, setPayerPhone] = useState('');
  const [payerName, setPayerName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const fetchQr = async () => {
    setLoadingQr(true);
    try {
      const { data } = await api.get('/wallet/qr', { responseType: 'blob' });
      setQrUrl(URL.createObjectURL(data));
    } catch {
      setError('Could not generate QR code.');
    } finally {
      setLoadingQr(false);
    }
  };

  const handleManualReceive = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/wallet/receive', {
        amount: parseFloat(amount),
        payer_phone: payerPhone,
        payer_name: payerName,
        description,
      });
      setSuccess(true);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Failed to record payment.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="px-5 pt-6 pb-4 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mt-16 mb-4">
          <ArrowDownLeft size={28} className="text-success" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Payment Received!</h2>
        <p className="text-gray-500 mb-1">{formatMYR(parseFloat(amount))}</p>
        <p className="text-sm text-gray-400 mb-8">Automatically recorded as Sales Revenue</p>
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
      <h1 className="text-xl font-bold text-gray-900 mb-5">Receive Payment</h1>

      {error && <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-xl mb-4">{error}</div>}

      {/* Mode Switcher */}
      <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
        <button
          onClick={() => { setMode('qr'); if (!qrUrl) fetchQr(); }}
          className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
            mode === 'qr' ? 'bg-white text-primary-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          Show QR Code
        </button>
        <button
          onClick={() => setMode('manual')}
          className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
            mode === 'manual' ? 'bg-white text-primary-500 shadow-sm' : 'text-gray-500'
          }`}
        >
          Record Manually
        </button>
      </div>

      {mode === 'qr' ? (
        <div className="text-center">
          {loadingQr ? (
            <div className="py-16"><Spinner className="mx-auto" /></div>
          ) : qrUrl ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 inline-block">
              <img src={qrUrl} alt="QR Code" className="w-56 h-56 mx-auto" />
            </div>
          ) : (
            <button
              onClick={fetchQr}
              className="bg-gray-50 rounded-2xl p-12 w-full flex flex-col items-center gap-3"
            >
              <QrCode size={48} className="text-gray-300" />
              <span className="text-sm text-gray-500">Tap to generate QR code</span>
            </button>
          )}
          <p className="text-sm text-gray-500 mt-4">Show this QR code to your customer to receive payment</p>
        </div>
      ) : (
        <form onSubmit={handleManualReceive} className="space-y-4">
          <p className="text-sm text-gray-500 mb-2">Record a cash or external payment you've received</p>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Customer Name (optional)</label>
            <input
              type="text"
              value={payerName}
              onChange={(e) => setPayerName(e.target.value)}
              placeholder="Customer name"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Customer Phone (optional)</label>
            <input
              type="tel"
              value={payerPhone}
              onChange={(e) => setPayerPhone(e.target.value)}
              placeholder="e.g. 60123456789"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Note (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Sold 5 nasi lemak"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <div className="bg-green-50 rounded-xl p-3">
            <p className="text-xs text-success font-medium">All incoming payments are automatically categorized as Sales Revenue</p>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-success text-white py-4 rounded-xl font-semibold text-lg disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? <><Spinner /> Recording...</> : `Record ${amount ? formatMYR(parseFloat(amount)) : 'Payment'}`}
          </button>
        </form>
      )}
    </div>
  );
}
