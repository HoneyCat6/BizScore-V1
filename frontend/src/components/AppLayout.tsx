import { Outlet } from 'react-router-dom';
import BottomNav from './BottomNav';

export default function AppLayout() {
  return (
    <div className="min-h-screen max-w-lg mx-auto bg-white relative pb-20">
      <Outlet />
      <BottomNav />
    </div>
  );
}
