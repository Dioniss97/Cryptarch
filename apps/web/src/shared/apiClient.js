import { getToken } from "./sessionStore";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

function normalizeApiError(status, data) {
  const detail = data?.detail;
  const details = data?.details;
  const code = data?.error?.code ?? data?.code ?? null;

  let message = "Error inesperado";
  if (typeof detail === "string") message = detail;
  else if (Array.isArray(detail) && detail.length > 0) message = detail[0]?.msg ?? message;
  else if (typeof data?.message === "string") message = data.message;

  return { status, message, code, details, detail, raw: data };
}

async function parseBody(response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiRequest(path, options = {}, config = {}) {
  const { skipAuth = false } = config;
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && options.body && typeof options.body === "string") {
    headers.set("Content-Type", "application/json");
  }
  if (!skipAuth && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const payload = await parseBody(response);
  if (!response.ok) {
    const error = normalizeApiError(response.status, payload);
    if (response.status === 401 && unauthorizedHandler) {
      unauthorizedHandler(error);
    }
    throw error;
  }
  return payload;
}

export const api = {
  get: (path) => apiRequest(path, { method: "GET" }),
  post: (path, body, config) =>
    apiRequest(
      path,
      { method: "POST", body: body ? JSON.stringify(body) : undefined },
      config,
    ),
  patch: (path, body) =>
    apiRequest(path, { method: "PATCH", body: JSON.stringify(body ?? {}) }),
  delete: (path) => apiRequest(path, { method: "DELETE" }),
};

export { API_BASE_URL };
