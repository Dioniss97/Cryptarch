import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";

const NAV_ITEMS = [
  ["users", "Users"],
  ["tags", "Tags"],
  ["filters", "Filters"],
  ["groups", "Groups"],
  ["connectors", "Connectors"],
  ["actions", "Actions"],
  ["documents", "Documents"],
];

export function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Admin</h2>
        <small>{user?.tenant_id}</small>
        <nav>
          {NAV_ITEMS.map(([path, label]) => (
            <NavLink
              key={path}
              to={`/admin/${path}`}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {label}
            </NavLink>
          ))}
          <NavLink to="/chat" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
            Chat
          </NavLink>
        </nav>
        <div style={{ marginTop: "20px" }}>
          <button
            onClick={async () => {
              await logout();
              navigate("/login");
            }}
          >
            Logout
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
