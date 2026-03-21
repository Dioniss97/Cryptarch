const baseConfig = {
  needsTags: false,
  needsFilters: false,
  beforeSave: (payload) => payload,
  toForm: (item) => ({ ...item }),
};

export const RESOURCE_CONFIGS = {
  tags: {
    ...baseConfig,
    title: "Tags",
    resource: "tags",
    columns: ["id", "name"],
    fields: [{ name: "name", label: "Name", type: "text" }],
    getInitialForm: () => ({ name: "" }),
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
        const rest = { ...payload };
        delete rest.target_type;
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
      {
        name: "user_filter_ids",
        label: "User filter ids",
        type: "multi-filter",
        filterKind: "user",
      },
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
};
