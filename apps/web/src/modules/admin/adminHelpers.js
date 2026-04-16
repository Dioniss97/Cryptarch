export function normalizeList(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
}

export function toJsonText(value) {
  if (value === undefined || value === null) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

export function parseJsonText(value, fieldName) {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value === "object") return value;
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`JSON invalido en ${fieldName}.`);
  }
}

export function pairsToRecord(pairs) {
  const result = {};
  for (const pair of pairs || []) {
    const key = String(pair.key || "").trim();
    if (!key) continue;
    result[key] = pair.value ?? "";
  }
  return result;
}

export function recordToPairs(record) {
  if (!record || typeof record !== "object") return [];
  return Object.entries(record).map(([key, value]) => ({
    key,
    value: value === undefined || value === null ? "" : String(value),
  }));
}

export function buildSchemaFromFields(fields) {
  const properties = {};
  const required = [];
  for (const field of fields || []) {
    const name = String(field.name || "").trim();
    if (!name) continue;
    properties[name] = {
      type: field.type || "string",
      description: field.description || "",
    };
    if (field.required) required.push(name);
  }
  return {
    type: "object",
    properties,
    required,
  };
}

export function extractSchemaFields(schema) {
  if (!schema || typeof schema !== "object") return [];
  const properties = schema.properties || {};
  const requiredSet = new Set(
    Array.isArray(schema.required) ? schema.required : [],
  );
  return Object.entries(properties).map(([name, definition]) => ({
    name,
    type: definition?.type || "string",
    description: definition?.description || "",
    required: requiredSet.has(name),
  }));
}

export function extractFileName(path) {
  if (!path) return "Documento";
  const normalized = String(path).replaceAll("\\", "/");
  const segments = normalized.split("/");
  return segments[segments.length - 1] || "Documento";
}

/** Resumen legible de auth_config del conector (para la lista y el panel). */
export function summarizeConnectorAuth(auth_config) {
  if (auth_config == null) return "Sin autenticación";
  if (typeof auth_config !== "object" || Object.keys(auth_config).length === 0)
    return "Sin autenticación";
  const t = auth_config.type;
  if (t === "bearer") {
    const env = auth_config.token_env;
    return env ? `Bearer (variable: ${env})` : "Bearer";
  }
  if (t === "api_key") {
    const hk = auth_config.header_name || "cabecera";
    return auth_config.key_env
      ? `API key en ${hk} (env: ${auth_config.key_env})`
      : `API key en ${hk}`;
  }
  if (t === "basic") {
    const username = auth_config.username;
    const passwordEnv = auth_config.password_env;
    if (username && passwordEnv) {
      return `Basic Auth (${username} / env: ${passwordEnv})`;
    }
    if (username) return `Basic Auth (${username})`;
    if (passwordEnv) return `Basic Auth (env: ${passwordEnv})`;
    return "Basic Auth";
  }
  if (t === "oauth2") {
    const parts = [];
    if (auth_config.client_id)
      parts.push(`client_id: ${auth_config.client_id}`);
    if (auth_config.token_url) parts.push("token URL");
    if (auth_config.scope || auth_config.scopes?.length) parts.push("scopes");
    return parts.length > 0 ? `OAuth2 (${parts.join(" · ")})` : "OAuth2";
  }
  return t === "custom"
    ? "JSON avanzado"
    : t
      ? `Auth tipo «${t}»`
      : "Autenticación personalizada";
}

export function emptyConnectorAuthFormFields() {
  return {
    authKind: "none",
    authBearerTokenEnv: "",
    authApiKeyHeader: "X-API-Key",
    authApiKeyKeyEnv: "",
    authBasicUsername: "",
    authBasicPasswordEnv: "",
    authOAuth2ClientId: "",
    authOAuth2ClientSecretEnv: "",
    authOAuth2TokenUrl: "",
    authOAuth2Scope: "",
    authCustomJson: "",
  };
}

/** Convierte auth_config de API a campos del formulario de conector. */
export function parseConnectorAuthForForm(auth_config) {
  const base = emptyConnectorAuthFormFields();
  if (auth_config == null) return base;
  if (typeof auth_config !== "object") {
    return {
      ...base,
      authKind: "custom",
      authCustomJson: toJsonText(auth_config),
    };
  }
  if (Object.keys(auth_config).length === 0) return base;
  const t = auth_config.type;
  if (t === "bearer") {
    return {
      ...base,
      authKind: "bearer",
      authBearerTokenEnv: String(auth_config.token_env ?? ""),
    };
  }
  if (t === "api_key") {
    return {
      ...base,
      authKind: "api_key",
      authApiKeyHeader: String(auth_config.header_name ?? "X-API-Key"),
      authApiKeyKeyEnv: String(auth_config.key_env ?? auth_config.env ?? ""),
    };
  }
  if (t === "oauth2") {
    const scopeValue = Array.isArray(auth_config.scopes)
      ? auth_config.scopes.join(" ")
      : auth_config.scope;
    return {
      ...base,
      authKind: "oauth2",
      authOAuth2ClientId: String(auth_config.client_id ?? ""),
      authOAuth2ClientSecretEnv: String(auth_config.client_secret_env ?? ""),
      authOAuth2TokenUrl: String(auth_config.token_url ?? ""),
      authOAuth2Scope: String(scopeValue ?? ""),
    };
  }
  if (t === "basic") {
    return {
      ...base,
      authKind: "basic",
      authBasicUsername: String(auth_config.username ?? ""),
      authBasicPasswordEnv: String(auth_config.password_env ?? ""),
    };
  }
  return {
    ...base,
    authKind: "custom",
    authCustomJson: JSON.stringify(auth_config, null, 2),
  };
}

/** Genera auth_config para PATCH/POST /admin/connectors. */
export function buildAuthConfigFromConnectorForm(form) {
  const kind = form.authKind;
  if (kind === "none") return null;
  if (kind === "custom") {
    const raw = form.authCustomJson?.trim();
    if (!raw) return null;
    return parseJsonText(raw, "auth_config");
  }
  if (kind === "bearer") {
    const o = { type: "bearer" };
    if (form.authBearerTokenEnv?.trim())
      o.token_env = form.authBearerTokenEnv.trim();
    return o;
  }
  if (kind === "api_key") {
    const o = { type: "api_key" };
    if (form.authApiKeyHeader?.trim())
      o.header_name = form.authApiKeyHeader.trim();
    if (form.authApiKeyKeyEnv?.trim()) o.key_env = form.authApiKeyKeyEnv.trim();
    return o;
  }
  if (kind === "basic") {
    const o = { type: "basic" };
    if (form.authBasicUsername?.trim())
      o.username = form.authBasicUsername.trim();
    if (form.authBasicPasswordEnv?.trim())
      o.password_env = form.authBasicPasswordEnv.trim();
    return o;
  }
  if (kind === "oauth2") {
    const o = { type: "oauth2", grant_type: "client_credentials" };
    if (form.authOAuth2ClientId?.trim())
      o.client_id = form.authOAuth2ClientId.trim();
    if (form.authOAuth2ClientSecretEnv?.trim())
      o.client_secret_env = form.authOAuth2ClientSecretEnv.trim();
    if (form.authOAuth2TokenUrl?.trim())
      o.token_url = form.authOAuth2TokenUrl.trim();
    if (form.authOAuth2Scope?.trim()) o.scope = form.authOAuth2Scope.trim();
    return o;
  }
  return null;
}

/** Une base URL del conector y path de la acción para vista previa (solo UI). */
export function joinBaseUrlAndPath(baseUrl, path) {
  const base = String(baseUrl || "").replace(/\/+$/, "");
  const p = String(path || "").trim();
  if (!p) return base || "—";
  if (p.startsWith("http://") || p.startsWith("https://")) return p;
  const suffix = p.startsWith("/") ? p : `/${p}`;
  if (!base) return suffix;
  return `${base}${suffix}`;
}
