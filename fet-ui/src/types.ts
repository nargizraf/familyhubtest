export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Category {
  id: string;
  name: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface Expense {
  id: string;
  amount: string;
  currency: string;
  description: string;
  category_id: string;
  category: string;
  date: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface Budget {
  amount: string | null;
  currency: string;
  month: string;
  spent: string;
  remaining: string | null;
  over_budget: boolean;
}

export interface CategorySpend {
  category_id: string;
  category: string;
  total: string;
}

export interface Dashboard {
  currency: string;
  month: string;
  current_month_spending: string;
  previous_month_spending: string;
  monthly_budget: string | null;
  remaining_budget: string | null;
  over_budget: boolean;
  expense_count: number;
  spending_by_category: CategorySpend[];
  recent_expenses: Expense[];
}

export interface ExpenseInput {
  amount: string;
  currency: string;
  description: string;
  category_id: string;
  date: string;
}
