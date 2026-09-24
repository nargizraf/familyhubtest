import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/expenses", label: "Expenses" },
  { to: "/categories", label: "Categories" },
  { to: "/settings", label: "Settings" },
];

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function onLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <NavLink to="/dashboard" className="brand">
          FamilyHub
        </NavLink>
        <nav>
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === "/dashboard"}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="userbox">
          <strong>{user?.full_name}</strong>
          <span>{user?.email}</span>
          <button type="button" className="button ghost" onClick={onLogout}>
            Log out
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
