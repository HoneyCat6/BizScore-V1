import { NavLink, useNavigate } from 'react-router-dom';
import { Home, Wallet, BarChart3, Award, MessageCircle, LogOut } from 'lucide-react';
import { useAuth } from '../lib/auth';

const navItems = [
  { to: '/dashboard', icon: Home, label: 'Home' },
  { to: '/wallet', icon: Wallet, label: 'Wallet' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/score', icon: Award, label: 'Score' },
  { to: '/chat', icon: MessageCircle, label: 'Chat' },
];

export default function BottomNav() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
      <div className="max-w-lg mx-auto flex items-center justify-around px-2 py-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 py-2 px-3 text-xs font-medium transition-colors ${
                isActive ? 'text-primary-500' : 'text-gray-400 hover:text-gray-600'
              }`
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
        <button
          onClick={handleLogout}
          className="flex flex-col items-center gap-0.5 py-2 px-3 text-xs font-medium text-gray-400 hover:text-danger transition-colors"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
}
