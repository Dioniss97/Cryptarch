function parseJsonField(value, fieldName) {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value === "object") return value;
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`JSON invalido en ${fieldName}.`);
  }
}

function toJsonTextarea(value) {
  if (value === undefined || value === null) return "";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

const baseConfig = {
  needsTags: false,
  needsFilters: false,
  beforeSave: (payload) => payload,
  toForm: (item) => ({ ...item }),
};

export const RESOURCE_CONFIGS = {
  users: {
    ...baseConfig,
    title: "Users",
    resource: "users",
    columns: ["id", "email", "role"],
    fields: [
      { name: "email", label: "Email", type: "email" },
      { name: "role", label: "Role", type: "select", options: ["admin", "user"] },
      { name: "password", label: "Password", type: "password" },
    ],
    getInitialForm: () => ({ email: "", role: "user", password: "" }),
  },
  tags: {
    ...baseConfig,
    title: "Tags",
    resource: "tags",
    columns: ["id", "name"],
    fields: [{ name: "name", label: "Name", type: "text" }],
    getInitialForm: () => ({ name: "" }),
  },
  connectors: {
    ...baseConfig,
    title: "Connectors",
    resource: "connectors",
    columns: ["id", "base_url", "auth_config"],
    fields: [
      { name: "base_url", label: "Base URL", type: "text" },
      { name: "auth_config", label: "Auth config JSON", type: "json-textarea" },
    ],
    getInitialForm: () => ({ base_url: "", auth_config: "" }),
    beforeSave: (payload) => ({
      ...payload,
      auth_config: parseJsonField(payload.auth_config, "auth_config"),
    }),
    toForm: (item) => ({ ...item, auth_config: toJsonTextarea(item.auth_config) }),
  },
  documents: {
    ...baseConfig,
    title: "Documents",
    resource: "documents",
    columns: ["id", "status", "file_path", "tag_ids"],
    needsTags: true,
    fields: [
      { name: "status", label: "Status", type: "text" },
      { name: "file_path", label: "File path", type: "text" },
      { name: "tag_ids", label: "Tags", type: "tag-picker" },
    ],
    getInitialForm: () => ({ status: "queued", file_path: "", tag_ids: [] }),
  },
  filters: {
    ...baseConfig,
    title: "Filters",
    resource: "filters",
    columns: ["id", "name", "target_type"],
    needsTags: true,
    fields: [
      { name: "name", label: "Name", type: "text" },
      {
        name: "target_type",
        label: "Target type",
        type: "select",
        options: ["user", "action", "document"],
      },
      { name: "tag_ids", label: "Tags (AND)", type: "tag-picker" },
    ],
    getInitialForm: () => ({ name: "", target_type: "user", tag_ids: [] }),
    beforeSave: (payload, ctx) => {
      if (ctx.isEditing) {
        const { target_type, ...rest } = payload;
        return rest;
      }
      return payload;
    },
  },
  groups: {
    ...baseConfig,
    title: "Groups",
    resource: "groups",
    columns: ["id", "name"],
    needsFilters: true,
    fields: [
      { name: "name", label: "Name", type: "text" },
      { name: "user_filter_ids", label: "User filter ids", type: "multi-filter", filterKind: "user" },
      {
        name: "action_filter_ids",
        label: "Action filter ids",
        type: "multi-filter",
        filterKind: "action",
      },
      {
        name: "document_filter_ids",
        label: "Document filter ids",
        type: "multi-filter",
        filterKind: "document",
      },
    ],
    getInitialForm: () => ({
      name: "",
      user_filter_ids: [],
      action_filter_ids: [],
      document_filter_ids: [],
    }),
  },
  actions: {
    ...baseConfig,
    title: "Actions",
    resource: "actions",
    columns: ["id", "name", "connector_id", "method", "path", "input_schema_version"],
    needsTags: true,
    fields: [
      { name: "connector_id", label: "Connector id", type: "text" },
      { name: "method", label: "Method", type: "text" },
      { name: "path", label: "Path", type: "text" },
      { name: "name", label: "Name", type: "text" },
      { name: "request_config", label: "Request config JSON", type: "json-textarea" },
      { name: "input_schema_json", label: "Input schema JSON", type: "json-textarea" },
      { name: "input_schema_version", label: "Schema version", type: "number" },
      { name: "tag_ids", label: "Tags", type: "tag-picker" },
    ],
    getInitialForm: () => ({
      connector_id: "",
      method: "POST",
      path: "",
      name: "",
      request_config: "",
      input_schema_json: "",
      input_schema_version: 1,
      tag_ids: [],
    }),
    beforeSave: (payload, ctx) => {
      const next = {
        ...payload,
        request_config: parseJsonField(payload.request_config, "request_config"),
        input_schema_json: parseJsonField(payload.input_schema_json, "input_schema_json"),
      };
      if (next.input_schema_version !== undefined) {
        next.input_schema_version = Number(next.input_schema_version);
      }
      if (ctx.isEditing) {
        const { connector_id, ...rest } = next;
        return rest;
      }
      return next;
    },
    toForm: (item) => ({
      ...item,
      request_config: toJsonTextarea(item.request_config),
      input_schema_json: toJsonTextarea(item.input_schema_json),
      input_schema_version:
        item.input_schema_version === null || item.input_schema_version === undefined
          ? ""
          : Number(item.input_schema_version),
      tag_ids: Array.isArray(item.tag_ids) ? item.tag_ids : [],
    }),
  },
};
