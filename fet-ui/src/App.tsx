import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute, PublicOnly } from "./components/ProtectedRoute";
import { CategoriesPage } from "./pages/Categories";
import { DashboardPage } from "./pages/Dashboard";
import { ExpenseFormPage } from "./pages/ExpenseForm";
import { ExpensesPage } from "./pages/Expenses";
import { LoginPage } from "./pages/Login";
import { RegisterPage } from "./pages/Register";
import { SettingsPage } from "./pages/Settings";

export function App() {
  return (
    <Routes>
      <Route element={<PublicOnly />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/expenses/new" element={<ExpenseFormPage />} />
          <Route path="/expenses/:id" element={<ExpenseFormPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
