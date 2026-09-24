import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth";

export function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="center">Loading…</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Outlet />;
}

export function PublicOnly() {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="center">Loading…</div>;
  }
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }
  return <Outlet />;
}
