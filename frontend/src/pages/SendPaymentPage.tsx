import { useState, useEffect, useRef, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Send, Package, Settings, Users, Home, Zap, TrendingUp, ShoppingCart, CreditCard, MoreHorizontal, QrCode, X } from 'lucide-react';
import { Html5QrcodeScanner } from 'html5-qrcode';
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

  // QR Scanner state
  const [scanning, setScanning] = useState(false);
  const [scannedName, setScannedName] = useState('');
  const [scanError, setScanError] = useState('');
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  const stopScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.clear().catch(() => {});
      scannerRef.current = null;
    }
    setScanning(false);
  };

  const startScanner = () => {
    setScanError('');
    setScanning(true);
  };

  useEffect(() => {
    if (!scanning) return;

    // Small delay to ensure the DOM element is rendered
    const timer = setTimeout(() => {
      const scanner = new Html5QrcodeScanner('qr-reader', {
        fps: 10,
        qrbox: { width: 250, height: 250 },
      }, false);

      scannerRef.current = scanner;

      scanner.render(
        (decodedText) => {
          try {
            const url = new URL(decodedText);
            const params = new URLSearchParams(url.search);
            const phone = params.get('phone') || '';
            const name = params.get('name') || '';
            const amt = params.get('amount') || '';

            if (phone) setRecipientPhone(phone);
            if (amt) setAmount(amt);
            if (name) setScannedName(name);

            scanner.clear().catch(() => {});
            scannerRef.current = null;
            setScanning(false);
          } catch {
            setScanError('Invalid QR code format.');
          }
        },
        (errorMessage) => {
          // Ignore scan-in-progress errors, only show permission issues
          if (errorMessage.includes('NotAllowedError') || errorMessage.includes('Permission')) {
            setScanError('Camera permission denied. Please allow camera access and try again.');
          }
        }
      );
    }, 100);

    return () => {
      clearTimeout(timer);
      if (scannerRef.current) {
        scannerRef.current.clear().catch(() => {});
        scannerRef.current = null;
      }
    };
  }, [scanning]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(() => {});
        scannerRef.current = null;
      }
    };
  }, []);

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

      {/* QR Scanner Section */}
      {!scanning ? (
        <button
          type="button"
          onClick={startScanner}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3.5 rounded-xl font-semibold flex items-center justify-center gap-2 mb-4 transition-colors"
        >
          <QrCode size={20} />
          Scan QR Code
        </button>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl p-4 mb-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-700">Scanning QR Code...</span>
            <button
              type="button"
              onClick={stopScanner}
              className="inline-flex items-center gap-1 text-sm text-red-500 font-medium hover:text-red-600"
            >
              <X size={16} /> Cancel
            </button>
          </div>
          {scanError && (
            <div className="bg-red-50 text-red-700 text-sm px-3 py-2 rounded-lg mb-3">{scanError}</div>
          )}
          <div id="qr-reader" className="rounded-xl overflow-hidden" />
        </div>
      )}

      {scannedName && (
        <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <Send size={14} className="text-success" />
          </div>
          <div>
            <p className="text-sm font-semibold text-green-800">Paying: {scannedName}</p>
            <p className="text-xs text-green-600">Scanned from QR code</p>
          </div>
        </div>
      )}

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
