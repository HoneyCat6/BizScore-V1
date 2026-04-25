import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './lib/auth';
import AppLayout from './components/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SendPaymentPage from './pages/SendPaymentPage';
import ReceivePaymentPage from './pages/ReceivePaymentPage';
import TransactionHistoryPage from './pages/TransactionHistoryPage';
import ReportsPage from './pages/ReportsPage';
import ScorePage from './pages/ScorePage';
import ScoreHistoryPage from './pages/ScoreHistoryPage';
import ChatPage from './pages/ChatPage';

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />

      {/* Protected routes with bottom nav */}
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/wallet/send" element={<SendPaymentPage />} />
        <Route path="/wallet/receive" element={<ReceivePaymentPage />} />
        <Route path="/transactions" element={<TransactionHistoryPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/score" element={<ScorePage />} />
        <Route path="/score/history" element={<ScoreHistoryPage />} />
        <Route path="/chat" element={<ChatPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
