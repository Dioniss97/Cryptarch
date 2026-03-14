import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";
import { ApiErrorBanner } from "../../shared/ui";

const INITIAL_FORM = {
  tenant_id: "",
  email: "",
  password: "",
};

export function LoginPage() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function onSubmit(event) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const session = await login(form);
      const fallback = session.user?.role === "admin" ? "/admin/users" : "/chat";
      navigate(location.state?.from?.pathname || fallback, { replace: true });
    } catch (nextError) {
      setError(nextError);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="panel">
        <h1>Acceso</h1>
        <p>Inicia sesión para entrar al panel admin o al chat.</p>
        <ApiErrorBanner error={error} />
        <form className="stack" onSubmit={onSubmit}>
          <label className="field">
            Tenant ID
            <input
              value={form.tenant_id}
              onChange={(event) => setForm((prev) => ({ ...prev, tenant_id: event.target.value }))}
              required
            />
          </label>
          <label className="field">
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
              required
            />
          </label>
          <label className="field">
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
              required
            />
          </label>
          <button className="primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
