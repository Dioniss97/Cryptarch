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
