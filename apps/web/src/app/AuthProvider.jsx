import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, apiRequest, setUnauthorizedHandler } from "../shared/apiClient";
import { clearSession, readSession, writeSession } from "../shared/sessionStore";

const AuthContext = createContext(null);

function decodeJwtClaims(token) {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(normalized);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => readSession());
  const [isBootstrapping, setIsBootstrapping] = useState(false);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearSession();
      setSession(null);
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  async function login(credentials) {
    const authPayload = await apiRequest(
      "/auth/login",
      { method: "POST", body: JSON.stringify(credentials) },
      { skipAuth: true },
    );

    const token = authPayload?.access_token;
    if (!token) throw { status: 500, message: "Respuesta de login inválida" };

    let profile;
    try {
      profile = await apiRequest(
        "/admin/me",
        { method: "GET", headers: { Authorization: `Bearer ${token}` } },
        { skipAuth: true },
      );
    } catch (error) {
      // Si /admin/me devuelve 403 para perfiles user, usamos claims del JWT.
      if (error?.status !== 403) throw error;
      profile = decodeJwtClaims(token);
    }

    if (!profile?.sub || !profile?.tenant_id || !profile?.role) {
      throw { status: 500, message: "No se pudo resolver el perfil de sesión." };
    }

    const nextSession = { token, user: profile };
    writeSession(nextSession);
    setSession(nextSession);
    return nextSession;
  }

  async function logout() {
    try {
      await api.post("/auth/logout");
    } catch {
      // no-op: limpiamos sesión local incluso si backend falla.
    } finally {
      clearSession();
      setSession(null);
    }
  }

  async function refreshMe() {
    if (!session?.token) return null;
    setIsBootstrapping(true);
    try {
      const profile = await api.get("/admin/me");
      const nextSession = { ...session, user: profile };
      writeSession(nextSession);
      setSession(nextSession);
      return profile;
    } finally {
      setIsBootstrapping(false);
    }
  }

  const value = useMemo(
    () => ({
      session,
      isAuthenticated: Boolean(session?.token),
      isAdmin: session?.user?.role === "admin",
      user: session?.user ?? null,
      isBootstrapping,
      login,
      logout,
      refreshMe,
    }),
    [session, isBootstrapping],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return context;
}
