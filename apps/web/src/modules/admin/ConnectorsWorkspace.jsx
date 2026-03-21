import { useEffect, useMemo, useState } from "react";
import { api } from "../../shared/apiClient";
import {
  ApiErrorBanner,
  ConfirmDelete,
  EmptyState,
  LoadingBlock,
} from "../../shared/ui";
import { ActionBuilderForm } from "./ActionBuilderForm";
import { normalizeList, parseJsonText, toJsonText } from "./adminHelpers";

function emptyConnectorForm() {
  return { base_url: "", auth_config: "" };
}

function connectorLabel(connector, index) {
  const url = connector?.base_url || "";
  return url ? `Conector ${index + 1}` : `Conector ${index + 1}`;
}

export function ConnectorsWorkspace() {
  const [connectors, setConnectors] = useState([]);
  const [actions, setActions] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedConnectorId, setSelectedConnectorId] = useState(null);
  const [connectorForm, setConnectorForm] = useState(emptyConnectorForm());
  const [editingConnectorId, setEditingConnectorId] = useState(null);
  const [editingAction, setEditingAction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingConnector, setSavingConnector] = useState(false);
  const [savingAction, setSavingAction] = useState(false);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [connectorsResult, actionsResult, tagsResult] = await Promise.all([
        api.get("/admin/connectors"),
        api.get("/admin/actions"),
        api.get("/admin/tags"),
      ]);
      const connectorsList = normalizeList(connectorsResult);
      setConnectors(connectorsList);
      setActions(normalizeList(actionsResult));
      setTags(normalizeList(tagsResult));
      setSelectedConnectorId((prev) => prev || connectorsList[0]?.id || null);
    } catch (nextError) {
      setError(nextError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const selectedConnector = useMemo(
    () => connectors.find((item) => item.id === selectedConnectorId) || null,
    [connectors, selectedConnectorId],
  );
  const connectorActions = useMemo(
    () =>
      actions.filter((action) => action.connector_id === selectedConnectorId),
    [actions, selectedConnectorId],
  );

  async function onCreateTag(name) {
    const payload = await api.post("/admin/tags", { name });
    const created = payload || { id: name, name };
    setTags((prev) => [created, ...prev]);
    return created;
  }

  async function onSaveConnector(event) {
    event.preventDefault();
    setSavingConnector(true);
    setError(null);
    try {
      const payload = {
        base_url: connectorForm.base_url,
        auth_config: parseJsonText(connectorForm.auth_config, "auth_config"),
      };
      if (editingConnectorId)
        await api.patch(`/admin/connectors/${editingConnectorId}`, payload);
      else await api.post("/admin/connectors", payload);
      setEditingConnectorId(null);
      setConnectorForm(emptyConnectorForm());
      await load();
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSavingConnector(false);
    }
  }

  async function onDeleteConnector(connectorId) {
    try {
      setError(null);
      await api.delete(`/admin/connectors/${connectorId}`);
      if (selectedConnectorId === connectorId) setSelectedConnectorId(null);
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  async function onSaveAction(payload) {
    if (!selectedConnectorId) return;
    setSavingAction(true);
    setError(null);
    try {
      if (editingAction?.id)
        await api.patch(`/admin/actions/${editingAction.id}`, payload);
      else
        await api.post("/admin/actions", {
          ...payload,
          connector_id: selectedConnectorId,
        });
      setEditingAction(null);
      await load();
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSavingAction(false);
    }
  }

  async function onDeleteAction(actionId) {
    try {
      setError(null);
      await api.delete(`/admin/actions/${actionId}`);
      await load();
    } catch (nextError) {
      setError(nextError);
    }
  }

  return (
    <div className="stack">
      <div className="page-header">
        <div>
          <h1>Conectores</h1>
          <p className="muted">
            Crea conectores HTTP y define sus acciones. Las acciones heredan la
            URL base y la autenticación del conector seleccionado.
          </p>
        </div>
        <button onClick={load}>Actualizar</button>
      </div>
      <ApiErrorBanner error={error} />

      <section className="panel">
        <h3>{editingConnectorId ? "Editar conector" : "Nuevo conector"}</h3>
        <form className="stack" onSubmit={onSaveConnector}>
          <div className="grid-2">
            <label className="field">
              Base URL
              <input
                required
                value={connectorForm.base_url}
                onChange={(event) =>
                  setConnectorForm((prev) => ({
                    ...prev,
                    base_url: event.target.value,
                  }))
                }
                placeholder="https://api.example.com"
              />
            </label>
            <label className="field">
              Auth config (JSON)
              <textarea
                rows={3}
                value={connectorForm.auth_config}
                onChange={(event) =>
                  setConnectorForm((prev) => ({
                    ...prev,
                    auth_config: event.target.value,
                  }))
                }
                placeholder='{"type":"bearer","token_env":"CRM_TOKEN"}'
              />
            </label>
          </div>
          <div className="row">
            <button
              className="primary"
              type="submit"
              disabled={savingConnector}
            >
              {savingConnector
                ? "Guardando..."
                : editingConnectorId
                  ? "Guardar cambios"
                  : "Crear conector"}
            </button>
            {editingConnectorId ? (
              <button
                type="button"
                onClick={() => {
                  setEditingConnectorId(null);
                  setConnectorForm(emptyConnectorForm());
                }}
              >
                Cancelar
              </button>
            ) : null}
          </div>
        </form>
      </section>

      <section className="panel connector-workspace-panel">
        <h3>Conector y acciones</h3>
        <p className="muted text-sm">
          Selecciona un conector para ver y gestionar sus acciones. Las acciones
          nuevas se crean dentro del conector seleccionado.
        </p>
        {loading ? <LoadingBlock /> : null}
        {!loading && connectors.length === 0 ? (
          <EmptyState
            title="No hay conectores"
            description="Crea el primer conector para empezar a definir actions."
          />
        ) : null}
        {!loading && connectors.length > 0 ? (
          <div className="split-layout">
            <aside className="connector-list">
              {connectors.map((connector, index) => (
                <button
                  type="button"
                  key={connector.id}
                  className={`connector-card${connector.id === selectedConnectorId ? " selected" : ""}`}
                  onClick={() => setSelectedConnectorId(connector.id)}
                >
                  <strong>{connectorLabel(connector, index)}</strong>
                  <small>{connector.base_url}</small>
                </button>
              ))}
            </aside>
            <div className="stack">
              {selectedConnector ? (
                <section className="panel subtle">
                  <div className="row spread">
                    <div>
                      <h4>{selectedConnector.base_url}</h4>
                      <small className="muted">
                        Auth heredada para actions de este conector.
                      </small>
                    </div>
                    <div className="row">
                      <button
                        type="button"
                        onClick={() => {
                          setEditingConnectorId(selectedConnector.id);
                          setConnectorForm({
                            base_url: selectedConnector.base_url || "",
                            auth_config: toJsonText(
                              selectedConnector.auth_config,
                            ),
                          });
                        }}
                      >
                        Editar conector
                      </button>
                      <ConfirmDelete
                        onConfirm={() =>
                          onDeleteConnector(selectedConnector.id)
                        }
                      />
                    </div>
                  </div>
                </section>
              ) : null}

              <section className="panel subtle">
                <h4>{editingAction ? "Editar acción" : "Nueva acción HTTP"}</h4>
                <ActionBuilderForm
                  initialAction={editingAction}
                  tags={tags}
                  saving={savingAction}
                  onSubmit={onSaveAction}
                  onCancel={() => setEditingAction(null)}
                  onCreateTag={onCreateTag}
                />
              </section>

              <section className="panel subtle">
                <h4>Acciones de este conector</h4>
                {connectorActions.length === 0 ? (
                  <EmptyState
                    title="Sin acciones"
                    description="Crea la primera acción con el formulario de arriba."
                  />
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Nombre</th>
                          <th>Metodo</th>
                          <th>Path</th>
                          <th>Version schema</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {connectorActions.map((action) => (
                          <tr key={action.id}>
                            <td>{action.name}</td>
                            <td>{action.method}</td>
                            <td>{action.path}</td>
                            <td>{action.input_schema_version ?? "-"}</td>
                            <td>
                              <div className="row">
                                <button
                                  type="button"
                                  onClick={() => setEditingAction(action)}
                                >
                                  Editar
                                </button>
                                <ConfirmDelete
                                  onConfirm={() => onDeleteAction(action.id)}
                                />
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}
