function emptyRow() {
  return { key: "", value: "" };
}

export function KeyValueListEditor({
  label,
  helperText,
  rows,
  onChange,
  valueLabel = "Valor",
}) {
  const safeRows = Array.isArray(rows) && rows.length > 0 ? rows : [emptyRow()];

  function updateRow(index, nextRow) {
    const next = safeRows.map((row, current) =>
      current === index ? nextRow : row,
    );
    onChange(next);
  }

  function removeRow(index) {
    const next = safeRows.filter((_, current) => current !== index);
    onChange(next.length > 0 ? next : [emptyRow()]);
  }

  return (
    <div className="stack">
      <div className="row spread">
        <strong>{label}</strong>
        <button
          type="button"
          onClick={() => {
            onChange([...safeRows, emptyRow()]);
          }}
        >
          Añadir fila
        </button>
      </div>
      {helperText ? <small className="muted">{helperText}</small> : null}
      <div className="stack dense">
        {safeRows.map((row, index) => (
          <div key={`${row.key}-${index}`} className="kv-row">
            <input
              placeholder="Clave"
              value={row.key ?? ""}
              onChange={(event) =>
                updateRow(index, { ...row, key: event.target.value })
              }
            />
            <input
              placeholder={valueLabel}
              value={row.value ?? ""}
              onChange={(event) =>
                updateRow(index, { ...row, value: event.target.value })
              }
            />
            <button type="button" onClick={() => removeRow(index)}>
              Quitar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
