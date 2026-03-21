import { useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";

export function ProfileMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <details className="profile-menu">
      <summary>
        <span className="profile-avatar">
          {(user?.sub || user?.email || "A").slice(0, 1).toUpperCase()}
        </span>
        <span>
          <strong>{user?.sub || "Cuenta"}</strong>
          <small>{user?.tenant_id || "tenant"}</small>
        </span>
      </summary>
      <div className="profile-popover">
        <button
          type="button"
          onClick={async () => {
            await logout();
            navigate("/login");
          }}
        >
          Cerrar sesion
        </button>
      </div>
    </details>
  );
}
