import { useEffect, useMemo, useState } from "react";
import { api } from "../../shared/apiClient";
import {
  ApiErrorBanner,
  ConfirmDelete,
  EmptyState,
  LoadingBlock,
  StatusBadge,
} from "../../shared/ui";
import { extractFileName, normalizeList } from "./adminHelpers";
import { TagPicker } from "./TagPicker";

function emptyForm() {
  return { status: "queued", file_path: "", tag_ids: [] };
}

export function DocumentsLibraryPage() {
  const [documents, setDocuments] = useState([]);
  const [tags, setTags] = useState([]);
  const [form, setForm] = useState(emptyForm());
  const [editingId, setEditingId] = useState(null);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [documentsResult, tagsResult] = await Promise.all([
        api.get("/admin/documents"),
        api.get("/admin/tags"),
      ]);
      setDocuments(normalizeList(documentsResult));
      setTags(normalizeList(tagsResult));
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onCreateTag(name) {
    const payload = await api.post("/admin/tags", { name });
    const created = payload || { id: name, name };
    setTags((prev) => [created, ...prev]);
    return created;
  }

  async function onSave(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        status: form.status,
        file_path: form.file_path,
        tag_ids: form.tag_ids,
      };
      if (editingId) await api.patch(`/admin/documents/${editingId}`, payload);
      else await api.post("/admin/documents", payload);
      setForm(emptyForm());
      setEditingId(null);
      await load();
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(documentId) {
    try {
      setError(null);
      await api.delete(`/admin/documents/${documentId}`);
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  const visibleDocuments = useMemo(() => {
    const term = query.trim().toLowerCase();
    return documents.filter((document) => {
      if (statusFilter !== "all" && document.status !== statusFilter)
        return false;
      if (
        term &&
        !String(document.file_path || "")
          .toLowerCase()
          .includes(term)
      )
        return false;
      return true;
    });
  }, [documents, query, statusFilter]);

  const tagIndex = useMemo(() => {
    const map = new Map();
    for (const tag of tags) map.set(tag.id ?? tag.name, tag.name || tag.id);
    return map;
  }, [tags]);

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1>Documentos</h1>
          <p className="muted">
            Tu biblioteca de documentos. Añade referencias, organiza con
            etiquetas y consulta el estado de cada uno.
          </p>
        </div>
        <button onClick={load}>Actualizar</button>
      </div>

      <ApiErrorBanner error={error} />

      <section className="panel">
        <h3>{editingId ? "Editar documento" : "Añadir documento"}</h3>
        <form className="stack" onSubmit={onSave}>
          <div className="grid-2">
            <label className="field">
              Título o nombre
              <input
                required
                value={form.file_path}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    file_path: event.target.value,
                  }))
                }
                placeholder="Ej: Manual de política RRHH"
              />
            </label>
            <label className="field">
              Estado
              <select
                value={form.status}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, status: event.target.value }))
                }
              >
                <option value="queued">En cola</option>
                <option value="processing">Procesando</option>
                <option value="indexed">Listo</option>
                <option value="error">Error</option>
              </select>
            </label>
          </div>
          <div className="field">
            <span>Etiquetas de contexto</span>
            <TagPicker
              options={tags}
              value={form.tag_ids}
              onChange={(next) =>
                setForm((prev) => ({ ...prev, tag_ids: next }))
              }
              onCreateTag={onCreateTag}
            />
          </div>
          <div className="row">
            <button className="primary" type="submit" disabled={saving}>
              {saving
                ? "Guardando…"
                : editingId
                  ? "Guardar cambios"
                  : "Añadir documento"}
            </button>
            {editingId ? (
              <button
                type="button"
                onClick={() => {
                  setEditingId(null);
                  setForm(emptyForm());
                }}
              >
                Cancelar
              </button>
            ) : null}
          </div>
        </form>
      </section>

      <section className="panel">
        <h3>Buscar en la biblioteca</h3>
        <div className="grid-2">
          <label className="field">
            Buscar
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="por título..."
            />
          </label>
          <label className="field">
            Estado
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="all">Todos</option>
              <option value="queued">En cola</option>
              <option value="processing">Procesando</option>
              <option value="indexed">Listo</option>
              <option value="error">Error</option>
            </select>
          </label>
        </div>
      </section>

      <section className="panel">
        {loading ? <LoadingBlock /> : null}
        {!loading && visibleDocuments.length === 0 ? (
          <EmptyState
            title="Sin documentos"
            description="Añade tu primer documento para que el chat pueda usarlo como referencia."
          />
        ) : null}
        {!loading && visibleDocuments.length > 0 ? (
          <div className="library-grid">
            {visibleDocuments.map((document) => (
              <article
                className="library-card"
                key={document.id || document.file_path}
              >
                <div className="row spread">
                  <h4>{extractFileName(document.file_path)}</h4>
                  <StatusBadge status={document.status} />
                </div>
                <p className="muted text-sm">{document.file_path}</p>
                <div className="row">
                  {(document.tag_ids || []).map((tagId) => (
                    <span className="badge" key={tagId}>
                      {tagIndex.get(tagId) || tagId}
                    </span>
                  ))}
                </div>
                <div className="row">
                  <button
                    type="button"
                    onClick={() => {
                      setEditingId(document.id);
                      setForm({
                        status: document.status || "queued",
                        file_path: document.file_path || "",
                        tag_ids: Array.isArray(document.tag_ids)
                          ? document.tag_ids
                          : [],
                      });
                    }}
                  >
                    Editar
                  </button>
                  <ConfirmDelete onConfirm={() => onDelete(document.id)} />
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
