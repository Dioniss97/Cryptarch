import { useEffect, useMemo, useState } from "react";
import { api } from "../../shared/apiClient";
import {
  ApiErrorBanner,
  ConfirmDelete,
  EmptyState,
  LoadingBlock,
} from "../../shared/ui";
import { ActionBuilderForm } from "./ActionBuilderForm";
import { AuthKindSelector } from "./AuthKindSelector";
import {
  buildAuthConfigFromConnectorForm,
  emptyConnectorAuthFormFields,
  normalizeList,
  parseConnectorAuthForForm,
  summarizeConnectorAuth,
} from "./adminHelpers";

function emptyConnectorForm() {
  return { base_url: "", ...emptyConnectorAuthFormFields() };
}

function connectorLabel(connector, index) {
  return `Conector ${index + 1}`;
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
        auth_config: buildAuthConfigFromConnectorForm(connectorForm),
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
          <label className="field connector-base-url-field">
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
            <p className="muted text-sm">
              Solo la base compartida del proveedor. Luego cada acción define su
              path específico.
            </p>
          </label>

          <div className="field connector-auth-field">
            <span>Autenticación del conector</span>
            <p className="muted text-sm">
              Esta pantalla persiste configuración reutilizable del conector. No
              implica que el runtime ya ejecute todos estos esquemas; hoy sirve
              para dejar la configuración guardada de forma clara y consistente.
            </p>
            <p className="muted text-sm">
              Las credenciales no se guardan aquí: indica nombres de variables
              de entorno o secretos del servidor, por ejemplo{" "}
              <code>CRM_API_TOKEN</code> o <code>CRM_CLIENT_SECRET</code>.
            </p>
            <AuthKindSelector
              value={connectorForm.authKind}
              onChange={(nextAuthKind) =>
                setConnectorForm((prev) => ({
                  ...prev,
                  authKind: nextAuthKind,
                }))
              }
            />
            {connectorForm.authKind === "none" ? (
              <div className="auth-kind-panel">
                <p className="muted text-sm">
                  El conector no aportará autenticación por defecto a sus
                  acciones.
                </p>
              </div>
            ) : null}
            {connectorForm.authKind === "bearer" ? (
              <div className="auth-kind-panel">
                <label className="field">
                  Variable de entorno del token
                  <input
                    value={connectorForm.authBearerTokenEnv}
                    onChange={(event) =>
                      setConnectorForm((prev) => ({
                        ...prev,
                        authBearerTokenEnv: event.target.value,
                      }))
                    }
                    placeholder="CRM_API_TOKEN"
                  />
                </label>
                <p className="muted text-sm">
                  Se guardará como{" "}
                  <code>{`{"type":"bearer","token_env":"..."}`}</code>.
                </p>
              </div>
            ) : null}
            {connectorForm.authKind === "api_key" ? (
              <div className="auth-kind-panel stack">
                <div className="grid-2">
                  <label className="field">
                    Nombre de la cabecera
                    <input
                      value={connectorForm.authApiKeyHeader}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authApiKeyHeader: event.target.value,
                        }))
                      }
                      placeholder="X-API-Key"
                    />
                  </label>
                  <label className="field">
                    Variable de entorno del valor
                    <input
                      value={connectorForm.authApiKeyKeyEnv}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authApiKeyKeyEnv: event.target.value,
                        }))
                      }
                      placeholder="MY_API_KEY"
                    />
                  </label>
                </div>
                <p className="muted text-sm">
                  Recomendado cuando el proveedor espera una cabecera propia en
                  vez de un bearer token estándar.
                </p>
              </div>
            ) : null}
            {connectorForm.authKind === "basic" ? (
              <div className="auth-kind-panel stack">
                <div className="grid-2">
                  <label className="field">
                    Username
                    <input
                      value={connectorForm.authBasicUsername}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authBasicUsername: event.target.value,
                        }))
                      }
                      placeholder="integrations-bot"
                    />
                  </label>
                  <label className="field">
                    Variable de entorno del password
                    <input
                      value={connectorForm.authBasicPasswordEnv}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authBasicPasswordEnv: event.target.value,
                        }))
                      }
                      placeholder="CRM_BASIC_PASSWORD"
                    />
                  </label>
                </div>
                <p className="muted text-sm">
                  Se persistirá como <code>username</code> +{" "}
                  <code>password_env</code> dentro de <code>auth_config</code>.
                </p>
              </div>
            ) : null}
            {connectorForm.authKind === "oauth2" ? (
              <div className="auth-kind-panel stack">
                <div className="grid-2">
                  <label className="field">
                    Client ID
                    <input
                      value={connectorForm.authOAuth2ClientId}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authOAuth2ClientId: event.target.value,
                        }))
                      }
                      placeholder="crm-client-id"
                    />
                  </label>
                  <label className="field">
                    Secret del cliente (env)
                    <input
                      value={connectorForm.authOAuth2ClientSecretEnv}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authOAuth2ClientSecretEnv: event.target.value,
                        }))
                      }
                      placeholder="CRM_CLIENT_SECRET"
                    />
                  </label>
                </div>
                <div className="grid-2">
                  <label className="field">
                    Token URL
                    <input
                      value={connectorForm.authOAuth2TokenUrl}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authOAuth2TokenUrl: event.target.value,
                        }))
                      }
                      placeholder="https://auth.example.com/oauth/token"
                    />
                  </label>
                  <label className="field">
                    Scope(s) opcional
                    <input
                      value={connectorForm.authOAuth2Scope}
                      onChange={(event) =>
                        setConnectorForm((prev) => ({
                          ...prev,
                          authOAuth2Scope: event.target.value,
                        }))
                      }
                      placeholder="contacts.read contacts.write"
                    />
                  </label>
                </div>
                <p className="muted text-sm">
                  Se guardará como OAuth2 guiado de tipo{" "}
                  <code>client_credentials</code>, con campos editables en{" "}
                  <code>auth_config</code>.
                </p>
              </div>
            ) : null}
            {connectorForm.authKind === "custom" ? (
              <div className="auth-kind-panel">
                <label className="field">
                  Auth config (JSON)
                  <textarea
                    rows={5}
                    value={connectorForm.authCustomJson}
                    onChange={(event) =>
                      setConnectorForm((prev) => ({
                        ...prev,
                        authCustomJson: event.target.value,
                      }))
                    }
                    placeholder='{"type":"oauth2","token_url":"https://...","extra":"..." }'
                  />
                </label>
                <p className="muted text-sm">
                  Úsalo solo si el método guiado no cubre tu caso. El backend lo
                  persistirá como JSON libre.
                </p>
              </div>
            ) : null}
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
                  <small className="muted connector-card-auth">
                    {summarizeConnectorAuth(connector.auth_config)}
                  </small>
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
                        {summarizeConnectorAuth(selectedConnector.auth_config)}
                      </small>
                    </div>
                    <div className="row">
                      <button
                        type="button"
                        onClick={() => {
                          setEditingConnectorId(selectedConnector.id);
                          setConnectorForm({
                            base_url: selectedConnector.base_url || "",
                            ...parseConnectorAuthForForm(
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
                  connectorBaseUrl={selectedConnector?.base_url}
                  connectorAuthSummary={summarizeConnectorAuth(
                    selectedConnector?.auth_config,
                  )}
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
                          <th>Método</th>
                          <th>Path</th>
                          <th>Versión del schema</th>
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
