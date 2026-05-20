function formatActionMeta(action) {
  const method =
    typeof action?.method === "string"
      ? action.method.trim().toUpperCase()
      : "";
  const pathStr = typeof action?.path === "string" ? action.path.trim() : "";
  if (!method && !pathStr) return null;
  return [method, pathStr].filter(Boolean).join(" ");
}

function schemaDescription(action) {
  const desc =
    typeof action?.input_schema_json?.description === "string"
      ? action.input_schema_json.description.trim()
      : "";
  return desc || null;
}

export function AllowedActionsList({ actions, selectedId, onSelect }) {
  return (
    <div className="connector-list" role="list">
      {actions.map((action) => {
        const id = action.id;
        const selected = id === selectedId;
        const meta = formatActionMeta(action);
        const description = schemaDescription(action);
        return (
          <button
            key={id}
            type="button"
            role="listitem"
            className={`connector-card panel subtle${selected ? " selected" : ""}`}
            onClick={() => onSelect(action)}
            style={{ cursor: "pointer", border: "1px solid #e5e7ef" }}
          >
            <strong style={{ fontSize: 14 }}>
              {action.name?.trim() || "Acción sin nombre"}
            </strong>
            {meta ? <span className="allowed-action-meta">{meta}</span> : null}
            {description ? (
              <span className="text-sm muted" style={{ lineHeight: 1.35 }}>
                {description}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
