export interface User {
  owner_id: string;
  name: string;
  business_name: string;
}

export interface OwnerProfile {
  owner_id: string;
  phone: string;
  name: string;
  business_name: string;
  business_type: string;
  location: string;
  wallet_balance: number;
  created_at: string;
}

export interface Transaction {
  txn_id: string;
  owner_id: string;
  amount: number;
  direction: 'inflow' | 'outflow';
  category: string;
  counterparty_phone: string;
  counterparty_name: string;
  description: string;
  txn_date: string;
  created_at: string;
}

export interface WalletBalance {
  balance: number;
  currency: string;
}

export interface PnLReport {
  period: string;
  revenue: number;
  cost_of_goods: number;
  gross_profit: number;
  operating_expenses: number;
  net_profit: number;
  expense_breakdown: Record<string, number>;
}

export interface CashFlowReport {
  period: string;
  operating_inflow: number;
  operating_outflow: number;
  capital_outflow: number;
  net_cash_flow: number;
}

export interface CategoryBreakdown {
  category: string;
  total: number;
  count: number;
  percentage: number;
}

export interface ScoreComponent {
  name: string;
  score: number;
  max_score: number;
  details: Record<string, unknown>;
}

export interface ScoreResult {
  score_id: string;
  owner_id: string;
  total_score: number;
  tier: string;
  components: ScoreComponent[];
  explanation: string;
  generated_at: string;
}

export const OUTFLOW_CATEGORIES = [
  { value: 'cost_of_goods', label: 'Cost of Goods', icon: 'Package' },
  { value: 'operating_expense', label: 'Operating Expense', icon: 'Settings' },
  { value: 'salary', label: 'Salary / Wages', icon: 'Users' },
  { value: 'rent', label: 'Rent', icon: 'Home' },
  { value: 'utilities', label: 'Utilities', icon: 'Zap' },
  { value: 'capital_expenditure', label: 'Capital Expenditure', icon: 'TrendingUp' },
  { value: 'asset_purchase', label: 'Asset Purchase', icon: 'ShoppingCart' },
  { value: 'loan_repayment', label: 'Loan Repayment', icon: 'CreditCard' },
  { value: 'other_expense', label: 'Other Expense', icon: 'MoreHorizontal' },
] as const;

export function tierColor(tier: string): string {
  switch (tier) {
    case 'Thriving': return '#059669';
    case 'Healthy': return '#1a56db';
    case 'Emerging': return '#d97706';
    case 'Early-Stage': return '#ea580c';
    case 'Pre-Launch': return '#6b7280';
    default: return '#6b7280';
  }
}

export function formatMYR(amount: number): string {
  return `RM ${amount.toFixed(2)}`;
}

export function formatCategory(cat: string): string {
  return cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
