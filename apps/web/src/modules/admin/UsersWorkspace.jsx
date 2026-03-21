import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../shared/apiClient";
import {
  ApiErrorBanner,
  ConfirmDelete,
  EmptyState,
  LoadingBlock,
} from "../../shared/ui";
import { normalizeList } from "./adminHelpers";
import { TagPicker } from "./TagPicker";

function emptyForm() {
  return { email: "", role: "user", password: "", tag_ids: [] };
}

function tagsById(tags) {
  const index = new Map();
  for (const tag of tags) {
    index.set(tag.id ?? tag.name, tag.name || tag.id);
  }
  return index;
}

function includesAll(source, expected) {
  const sourceSet = new Set(Array.isArray(source) ? source : []);
  return (expected || []).every((tagId) => sourceSet.has(tagId));
}

export function UsersWorkspace() {
  const [users, setUsers] = useState([]);
  const [tags, setTags] = useState([]);
  const [filters, setFilters] = useState([]);
  const [form, setForm] = useState(emptyForm());
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [tagFilter, setTagFilter] = useState([]);
  const [newFilterName, setNewFilterName] = useState("");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [usersResult, tagsResult, filtersResult] = await Promise.all([
        api.get("/admin/users"),
        api.get("/admin/tags"),
        api.get("/admin/filters"),
      ]);
      setUsers(normalizeList(usersResult));
      setTags(normalizeList(tagsResult));
      setFilters(
        normalizeList(filtersResult).filter(
          (item) => item.target_type === "user",
        ),
      );
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const tagIndex = useMemo(() => tagsById(tags), [tags]);
  const filteredUsers = useMemo(() => {
    const term = search.trim().toLowerCase();
    return users.filter((user) => {
      const userTags = Array.isArray(user.tag_ids) ? user.tag_ids : [];
      if (roleFilter !== "all" && user.role !== roleFilter) return false;
      if (
        term &&
        !String(user.email || "")
          .toLowerCase()
          .includes(term)
      )
        return false;
      if (!includesAll(userTags, tagFilter)) return false;
      return true;
    });
  }, [roleFilter, search, tagFilter, users]);

  async function onCreateTag(name) {
    const payload = await api.post("/admin/tags", { name });
    const created = payload || { id: name, name };
    setTags((prev) => [created, ...prev]);
    return created;
  }

  async function onSaveUser(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        email: form.email,
        role: form.role,
        ...(form.password ? { password: form.password } : {}),
        tag_ids: Array.isArray(form.tag_ids) ? form.tag_ids : [],
      };
      if (editingId) await api.patch(`/admin/users/${editingId}`, payload);
      else await api.post("/admin/users", payload);
      setEditingId(null);
      setForm(emptyForm());
      await load();
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSaving(false);
    }
  }

  async function onDeleteUser(userId) {
    try {
      setError(null);
      await api.delete(`/admin/users/${userId}`);
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  async function onSaveFilter() {
    if (!newFilterName.trim()) return;
    try {
      setError(null);
      await api.post("/admin/filters", {
        name: newFilterName.trim(),
        target_type: "user",
        tag_ids: tagFilter,
      });
      setNewFilterName("");
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1>Usuarios</h1>
          <p className="muted">
            Gestiona usuarios, filtra en vivo y guarda filtros para usarlos en
            grupos.
          </p>
        </div>
        <button onClick={load}>Actualizar</button>
      </div>

      <ApiErrorBanner error={error} />

      <section className="panel">
        <h3>{editingId ? "Editar usuario" : "Crear usuario"}</h3>
        <form className="stack" onSubmit={onSaveUser}>
          <div className="grid-3">
            <label className="field">
              Email
              <input
                required
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, email: event.target.value }))
                }
              />
            </label>
            <label className="field">
              Rol
              <select
                value={form.role}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, role: event.target.value }))
                }
              >
                <option value="admin">admin</option>
                <option value="user">user</option>
              </select>
            </label>
            <label className="field">
              Password {editingId ? "(opcional)" : ""}
              <input
                type="password"
                value={form.password}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, password: event.target.value }))
                }
              />
            </label>
          </div>
          <div className="field">
            <span>Tags del usuario</span>
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
                ? "Guardando..."
                : editingId
                  ? "Guardar cambios"
                  : "Crear usuario"}
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
        <h3>Filtro en vivo</h3>
        <p className="muted text-sm">
          Filtra la tabla al instante. Puedes guardar el filtro actual para
          reutilizarlo en grupos (se crea en /admin/filters con
          target_type=user).
        </p>
        <div className="grid-3">
          <label className="field">
            Buscar por email
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="admin@"
            />
          </label>
          <label className="field">
            Rol
            <select
              value={roleFilter}
              onChange={(event) => setRoleFilter(event.target.value)}
            >
              <option value="all">Todos</option>
              <option value="admin">admin</option>
              <option value="user">user</option>
            </select>
          </label>
          <label className="field">
            Guardar filtro
            <div className="row">
              <input
                value={newFilterName}
                placeholder="Ej: Admins con permisos"
                onChange={(event) => setNewFilterName(event.target.value)}
              />
              <button type="button" onClick={onSaveFilter} className="primary">
                Guardar
              </button>
            </div>
          </label>
        </div>
        <div className="field">
          <span>Tags obligatorios (AND)</span>
          <TagPicker
            options={tags}
            value={tagFilter}
            onChange={setTagFilter}
            onCreateTag={onCreateTag}
          />
        </div>
        {filters.length > 0 ? (
          <div className="row">
            <small className="muted">Filtros guardados para usuarios:</small>
            {filters.map((filter) => (
              <button
                type="button"
                key={filter.id || filter.name}
                onClick={() =>
                  setTagFilter(
                    Array.isArray(filter.tag_ids) ? filter.tag_ids : [],
                  )
                }
              >
                {filter.name}
              </button>
            ))}
            <Link to="/admin/filters" className="link-muted">
              Ver filtros guardados →
            </Link>
          </div>
        ) : (
          <div className="row">
            <Link to="/admin/filters" className="link-muted text-sm">
              Ver filtros guardados en /admin/filters
            </Link>
          </div>
        )}
      </section>

      <section className="panel">
        <h3>Usuarios ({filteredUsers.length})</h3>
        {loading ? <LoadingBlock /> : null}
        {!loading && filteredUsers.length === 0 ? (
          <EmptyState
            title="Sin usuarios"
            description="Ajusta filtros o crea el primer usuario."
          />
        ) : null}
        {!loading && filteredUsers.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Tags</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id || user.email}>
                    <td>{user.email}</td>
                    <td>{user.role}</td>
                    <td>
                      <div className="row">
                        {(user.tag_ids || []).map((tagId) => (
                          <span className="badge" key={tagId}>
                            {tagIndex.get(tagId) || tagId}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="row">
                        <button
                          type="button"
                          onClick={() => {
                            setEditingId(user.id);
                            setForm({
                              email: user.email || "",
                              role: user.role || "user",
                              password: "",
                              tag_ids: Array.isArray(user.tag_ids)
                                ? user.tag_ids
                                : [],
                            });
                          }}
                        >
                          Editar
                        </button>
                        <ConfirmDelete
                          onConfirm={() => onDeleteUser(user.id)}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </div>
  );
}
