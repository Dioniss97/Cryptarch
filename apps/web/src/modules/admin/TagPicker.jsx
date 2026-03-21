import { useCallback, useMemo, useState } from "react";

export function TagPicker({ options, value, onChange, onCreateTag }) {
  const [draftName, setDraftName] = useState("");
  const [creating, setCreating] = useState(false);
  const [focused, setFocused] = useState(false);
  const selected = useMemo(() => new Set(value || []), [value]);
  const normalizedOptions = useMemo(() => options || [], [options]);

  const handleAddExisting = useCallback(
    (tagId) => {
      if (selected.has(tagId)) return;
      onChange([...(value || []), tagId]);
    },
    [value, onChange, selected],
  );

  const handleCreate = useCallback(async () => {
    const nextName = draftName.trim();
    if (!nextName || !onCreateTag) return;
    const existing = normalizedOptions.find(
      (t) =>
        String(t.name || t.id || "").toLowerCase() === nextName.toLowerCase(),
    );
    if (existing) {
      handleAddExisting(existing.id ?? existing.name);
      setDraftName("");
      return;
    }
    setCreating(true);
    try {
      const created = await onCreateTag(nextName);
      const nextId = created?.id ?? created?.name ?? nextName;
      if (!selected.has(nextId)) onChange([...(value || []), nextId]);
      setDraftName("");
    } finally {
      setCreating(false);
    }
  }, [
    draftName,
    onCreateTag,
    normalizedOptions,
    handleAddExisting,
    selected,
    value,
    onChange,
  ]);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && draftName.trim()) {
      event.preventDefault();
      handleCreate();
    }
  };

  const availableTags = normalizedOptions.filter((tag) => {
    const tagValue = tag.id ?? tag.name;
    return !selected.has(tagValue);
  });

  const datalistId = useMemo(
    () => `tag-picker-dl-${Math.random().toString(36).slice(2)}`,
    [],
  );

  return (
    <div
      className={`tag-picker stack dense${focused ? " focused" : ""}`}
      role="group"
      aria-label="Seleccionar o crear tags"
    >
      <div className="tag-picker-selected row">
        {normalizedOptions
          .filter((tag) => selected.has(tag.id ?? tag.name))
          .map((tag) => {
            const tagValue = tag.id ?? tag.name;
            return (
              <span key={tagValue} className="badge badge-selected">
                {tag.name || tagValue}
                <button
                  type="button"
                  className="badge-remove"
                  onClick={() =>
                    onChange((value || []).filter((id) => id !== tagValue))
                  }
                  aria-label={`Quitar ${tag.name || tagValue}`}
                >
                  ×
                </button>
              </span>
            );
          })}
      </div>
      {availableTags.length > 0 && (
        <div className="tag-picker-available row">
          {availableTags.slice(0, 12).map((tag) => {
            const tagValue = tag.id ?? tag.name;
            return (
              <button
                key={tagValue}
                type="button"
                className="badge badge-available"
                onClick={() => handleAddExisting(tagValue)}
                aria-label={`Añadir ${tag.name || tagValue}`}
              >
                + {tag.name || tagValue}
              </button>
            );
          })}
        </div>
      )}
      {onCreateTag ? (
        <div className={`tag-picker-create row${focused ? " focused" : ""}`}>
          <input
            value={draftName}
            placeholder="Nueva tag"
            onChange={(event) => setDraftName(event.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            list={availableTags.length > 0 ? datalistId : undefined}
            aria-label="Crear o seleccionar tag"
          />
          {availableTags.length > 0 ? (
            <datalist id={datalistId}>
              {availableTags.map((tag) => (
                <option key={tag.id ?? tag.name} value={tag.name || tag.id} />
              ))}
            </datalist>
          ) : null}
          <button
            type="button"
            onClick={handleCreate}
            disabled={creating || !draftName.trim()}
            className="primary"
            aria-label="Crear tag"
          >
            {creating ? "Creando…" : "Crear tag"}
          </button>
        </div>
      ) : null}
    </div>
  );
}
