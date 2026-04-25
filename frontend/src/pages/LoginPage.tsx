import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, ChevronLeft } from 'lucide-react';
import api from '../lib/api';
import { useAuth } from '../lib/auth';
import { Spinner } from '../components/Spinner';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phone, setPhone] = useState('');
  const [pin, setPin] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/login', { phone, pin });
      login(data.access_token, {
        owner_id: data.owner_id,
        name: data.name,
        business_name: data.business_name,
      });
      navigate('/dashboard');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Login failed. Check your phone and PIN.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen max-w-lg mx-auto bg-white px-6 py-8">
      <Link to="/" className="inline-flex items-center text-gray-500 text-sm mb-6 hover:text-gray-700">
        <ChevronLeft size={18} /> Back
      </Link>

      <div className="flex items-center gap-3 mb-10">
        <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
          <Shield size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Welcome Back</h1>
          <p className="text-sm text-gray-500">Log in to your BizScore account</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm px-4 py-3 rounded-xl mb-4">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input
            type="tel"
            required
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="e.g. 60123456789"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">PIN</label>
          <input
            type="password"
            required
            maxLength={6}
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            placeholder="Enter your PIN"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-lg tracking-widest"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-500 text-white py-4 rounded-xl font-semibold text-lg hover:bg-primary-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mt-6"
        >
          {loading ? <><Spinner /> Logging in...</> : 'Log In'}
        </button>
      </form>

      <div className="mt-8 p-4 bg-gray-50 rounded-xl">
        <p className="text-xs text-gray-500 font-medium mb-2">Demo Accounts (PIN: 1234)</p>
        <div className="space-y-1 text-xs text-gray-500">
          <p><span className="font-mono">60123456001</span> - Maria (Market Vendor)</p>
          <p><span className="font-mono">60123456002</span> - James (Boda-boda Rider)</p>
          <p><span className="font-mono">60123456003</span> - Aisha (Tailor)</p>
        </div>
      </div>

      <p className="text-center text-sm text-gray-500 mt-6">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-500 font-medium">Sign up</Link>
      </p>
    </div>
  );
}
