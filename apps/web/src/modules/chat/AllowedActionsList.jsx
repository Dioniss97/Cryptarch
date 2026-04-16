function actionSubtitle(action) {
  const desc =
    typeof action?.input_schema_json?.description === "string"
      ? action.input_schema_json.description.trim()
      : "";
  if (desc) return desc;
  return null;
}

export function AllowedActionsList({ actions, selectedId, onSelect }) {
  return (
    <div className="connector-list" role="list">
      {actions.map((action) => {
        const id = action.id;
        const selected = id === selectedId;
        const subtitle = actionSubtitle(action);
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
            {subtitle ? (
              <span className="text-sm muted" style={{ lineHeight: 1.35 }}>
                {subtitle}
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
