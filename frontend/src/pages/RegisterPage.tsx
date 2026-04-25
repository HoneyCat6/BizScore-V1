import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, ChevronLeft } from 'lucide-react';
import api from '../lib/api';
import { useAuth } from '../lib/auth';
import { Spinner } from '../components/Spinner';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    phone: '',
    pin: '',
    name: '',
    business_name: '',
    business_type: '',
    location: '',
  });

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/auth/register', form);
      login(data.access_token, {
        owner_id: data.owner_id,
        name: data.name,
        business_name: data.business_name,
      });
      navigate('/dashboard');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen max-w-lg mx-auto bg-white px-6 py-8">
      <Link to="/" className="inline-flex items-center text-gray-500 text-sm mb-6 hover:text-gray-700">
        <ChevronLeft size={18} /> Back
      </Link>

      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
          <Shield size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Create Account</h1>
          <p className="text-sm text-gray-500">Start building your business score</p>
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
            value={form.phone}
            onChange={set('phone')}
            placeholder="e.g. 60123456789"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">PIN (4-6 digits)</label>
          <input
            type="password"
            required
            maxLength={6}
            value={form.pin}
            onChange={set('pin')}
            placeholder="Enter your PIN"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-lg tracking-widest"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
          <input
            type="text"
            required
            value={form.name}
            onChange={set('name')}
            placeholder="Full name"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
          <input
            type="text"
            required
            value={form.business_name}
            onChange={set('business_name')}
            placeholder="e.g. Maria's Market Stall"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
          <input
            type="text"
            required
            value={form.business_type}
            onChange={set('business_type')}
            placeholder="e.g. Food Vendor, Tailor, Transport"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location (optional)</label>
          <input
            type="text"
            value={form.location}
            onChange={set('location')}
            placeholder="e.g. Petaling Jaya"
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-500 text-white py-4 rounded-xl font-semibold text-lg hover:bg-primary-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mt-6"
        >
          {loading ? <><Spinner /> Creating...</> : 'Create Account'}
        </button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-500 font-medium">Log in</Link>
      </p>
    </div>
  );
}
