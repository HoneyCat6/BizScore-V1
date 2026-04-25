import { Link } from 'react-router-dom';
import { Shield, TrendingUp, FileText, Wallet } from 'lucide-react';

const features = [
  { icon: Wallet, title: 'E-Wallet', desc: 'Send and receive payments instantly with your business wallet' },
  { icon: TrendingUp, title: 'Auto Accounting', desc: 'Every transaction is automatically tracked and categorized' },
  { icon: Shield, title: 'Business Score', desc: 'Get a performance score (0-850) based on your real business data' },
  { icon: FileText, title: 'Loan Report', desc: 'Generate a professional report to apply for loans anywhere' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen max-w-lg mx-auto bg-white">
      {/* Hero */}
      <div className="bg-gradient-to-br from-primary-500 to-primary-800 text-white px-6 pt-16 pb-20 text-center">
        <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Shield size={32} className="text-white" />
        </div>
        <h1 className="text-3xl font-bold mb-3">BizScore</h1>
        <p className="text-lg text-primary-100 leading-relaxed">
          Your business wallet.<br />
          Your business score.<br />
          Your future.
        </p>
      </div>

      {/* Features */}
      <div className="px-6 -mt-8">
        <div className="bg-white rounded-2xl shadow-lg p-6 space-y-5">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex gap-4">
              <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center shrink-0">
                <Icon size={20} className="text-primary-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{title}</h3>
                <p className="text-sm text-gray-500 mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="px-6 py-10 space-y-3">
        <Link
          to="/register"
          className="block w-full bg-primary-500 text-white text-center py-4 rounded-xl font-semibold text-lg hover:bg-primary-600 transition-colors"
        >
          Get Started
        </Link>
        <Link
          to="/login"
          className="block w-full bg-gray-100 text-gray-700 text-center py-4 rounded-xl font-semibold text-lg hover:bg-gray-200 transition-colors"
        >
          I already have an account
        </Link>
      </div>

      <p className="text-center text-xs text-gray-400 pb-8 px-6">
        Empowering small businesses with financial inclusion
      </p>
    </div>
  );
}
