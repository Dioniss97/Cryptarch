import { useEffect, useMemo, useState } from "react";
import { api } from "../../shared/apiClient";
import { ApiErrorBanner, ConfirmDelete, EmptyState, LoadingBlock, StatusBadge } from "../../shared/ui";
import { TagPicker } from "./TagPicker";

function normalizeList(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
}

function compactPayload(fields, source) {
  const payload = {};
  for (const field of fields) {
    const value = source[field.name];
    if (value === "" || value === undefined) continue;
    payload[field.name] = value;
  }
  return payload;
}

function fieldToString(value) {
  if (value === null || value === undefined) return "-";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function CrudPage({ config }) {
  const [items, setItems] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState([]);
  const [form, setForm] = useState(config.getInitialForm());
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const isEditing = Boolean(editingId);
  const endpoint = `/admin/${config.resource}`;

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [list, tagsResult, filtersResult] = await Promise.all([
        api.get(endpoint),
        config.needsTags ? api.get("/admin/tags") : Promise.resolve([]),
        config.needsFilters ? api.get("/admin/filters") : Promise.resolve([]),
      ]);
      setItems(normalizeList(list));
      setTags(normalizeList(tagsResult));
      setFilters(normalizeList(filtersResult));
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config.resource]);

  const filtersByType = useMemo(() => {
    return {
      user: filters.filter((item) => item.target_type === "user"),
      action: filters.filter((item) => item.target_type === "action"),
      document: filters.filter((item) => item.target_type === "document"),
    };
  }, [filters]);

  function startCreate() {
    setEditingId(null);
    setForm(config.getInitialForm());
  }

  function startEdit(item) {
    setEditingId(item.id);
    setForm(config.toForm(item));
  }

  async function onSave(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = config.beforeSave(compactPayload(config.fields, form), { isEditing });
      if (isEditing) await api.patch(`${endpoint}/${editingId}`, payload);
      else await api.post(endpoint, payload);
      startCreate();
      await load();
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(item) {
    try {
      setError(null);
      await api.delete(`${endpoint}/${item.id}`);
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1>{config.title}</h1>
        <div className="row">
          <button onClick={load}>Refrescar</button>
          <button className="primary" onClick={startCreate}>
            Nuevo
          </button>
        </div>
      </div>

      <ApiErrorBanner error={error} />

      <section className="panel">
        <h3>{isEditing ? "Editar" : "Crear"}</h3>
        <form onSubmit={onSave} className="stack">
          {config.fields.map((field) => {
            const value = form[field.name];
            if (field.type === "tag-picker") {
              return (
                <div key={field.name} className="field">
                  <span>{field.label}</span>
                  <TagPicker
                    options={tags}
                    value={Array.isArray(value) ? value : []}
                    onChange={(next) => setForm((prev) => ({ ...prev, [field.name]: next }))}
                  />
                  <small>Semántica AND: deben cumplirse todos los tags.</small>
                </div>
              );
            }

            if (field.type === "multi-filter") {
              const options = filtersByType[field.filterKind] || [];
              const selected = Array.isArray(value) ? value : [];
              return (
                <label key={field.name} className="field">
                  {field.label}
                  <select
                    multiple
                    value={selected}
                    onChange={(event) => {
                      const next = Array.from(event.target.selectedOptions).map((opt) => opt.value);
                      setForm((prev) => ({ ...prev, [field.name]: next }));
                    }}
                  >
                    {options.map((option) => (
                      <option key={option.id} value={option.id}>
                        {option.name || option.id}
                      </option>
                    ))}
                  </select>
                </label>
              );
            }

            if (field.type === "select") {
              return (
                <label key={field.name} className="field">
                  {field.label}
                  <select
                    value={value ?? ""}
                    onChange={(event) => setForm((prev) => ({ ...prev, [field.name]: event.target.value }))}
                  >
                    <option value="">--</option>
                    {field.options.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              );
            }

            if (field.type === "number") {
              return (
                <label key={field.name} className="field">
                  {field.label}
                  <input
                    type="number"
                    value={value ?? ""}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        [field.name]: event.target.value === "" ? "" : Number(event.target.value),
                      }))
                    }
                  />
                </label>
              );
            }

            if (field.type === "json-textarea") {
              return (
                <label key={field.name} className="field">
                  {field.label}
                  <textarea
                    rows={6}
                    value={value ?? ""}
                    onChange={(event) => setForm((prev) => ({ ...prev, [field.name]: event.target.value }))}
                  />
                </label>
              );
            }

            if (field.type === "textarea") {
              return (
                <label key={field.name} className="field">
                  {field.label}
                  <textarea
                    rows={3}
                    value={value ?? ""}
                    onChange={(event) => setForm((prev) => ({ ...prev, [field.name]: event.target.value }))}
                  />
                </label>
              );
            }

            return (
              <label key={field.name} className="field">
                {field.label}
                <input
                  type={field.type || "text"}
                  value={value ?? ""}
                  onChange={(event) => setForm((prev) => ({ ...prev, [field.name]: event.target.value }))}
                />
              </label>
            );
          })}
          <div className="row">
            <button className="primary" type="submit" disabled={saving}>
              {saving ? "Guardando..." : isEditing ? "Guardar cambios" : "Crear"}
            </button>
            {isEditing ? <button onClick={startCreate}>Cancelar edición</button> : null}
          </div>
        </form>
      </section>

      <section className="panel">
        <h3>Listado</h3>
        {loading ? <LoadingBlock /> : null}
        {!loading && items.length === 0 ? (
          <EmptyState title="Sin registros" description="No hay elementos todavía." />
        ) : null}
        {!loading && items.length > 0 ? (
          <table>
            <thead>
              <tr>
                {config.columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id || JSON.stringify(item)}>
                  {config.columns.map((column) => (
                    <td key={column}>
                      {column === "status" ? (
                        <StatusBadge status={item[column]} />
                      ) : (
                        fieldToString(item[column])
                      )}
                    </td>
                  ))}
                  <td>
                    <div className="row">
                      <button onClick={() => startEdit(item)}>Editar</button>
                      <ConfirmDelete onConfirm={() => onDelete(item)} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </section>
    </div>
  );
}
