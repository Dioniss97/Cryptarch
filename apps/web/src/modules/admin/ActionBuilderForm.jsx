import { useEffect, useMemo, useState } from "react";
import { TagPicker } from "./TagPicker";
import { KeyValueListEditor } from "./KeyValueListEditor";
import {
  buildSchemaFromFields,
  extractSchemaFields,
  joinBaseUrlAndPath,
  pairsToRecord,
  recordToPairs,
} from "./adminHelpers";

const METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"];
const FIELD_TYPES = ["string", "number", "integer", "boolean"];

function ensureSchemaRows(rows) {
  if (Array.isArray(rows) && rows.length > 0) return rows;
  return [{ name: "", type: "string", description: "", required: false }];
}

function initialState(initialAction) {
  const requestConfig = initialAction?.request_config || {};
  const timeoutRaw = requestConfig?.timeout;
  return {
    name: initialAction?.name || "",
    method: (initialAction?.method || "POST").toUpperCase(),
    path: initialAction?.path || "",
    contentType: requestConfig?.content_type || "application/json",
    useConnectorAuth: requestConfig?.auth?.mode !== "none",
    headers: recordToPairs(requestConfig?.headers),
    queryParams: recordToPairs(requestConfig?.query_params),
    bodyParams: recordToPairs(requestConfig?.body_params),
    timeoutSec:
      timeoutRaw !== undefined && timeoutRaw !== null && timeoutRaw !== ""
        ? String(timeoutRaw)
        : "",
    inputSchemaVersion:
      initialAction?.input_schema_version === undefined ||
      initialAction?.input_schema_version === null
        ? 1
        : Number(initialAction.input_schema_version),
    schemaFields: ensureSchemaRows(
      extractSchemaFields(initialAction?.input_schema_json),
    ),
    tag_ids: Array.isArray(initialAction?.tag_ids) ? initialAction.tag_ids : [],
  };
}

export function ActionBuilderForm({
  initialAction,
  connectorBaseUrl,
  connectorAuthSummary,
  tags,
  saving,
  onSubmit,
  onCancel,
  onCreateTag,
}) {
  const [form, setForm] = useState(() => initialState(initialAction));
  useEffect(() => {
    setForm(initialState(initialAction));
  }, [initialAction]);

  const hasBody = useMemo(
    () =>
      ["POST", "PUT", "PATCH"].includes(
        String(form.method || "").toUpperCase(),
      ),
    [form.method],
  );

  const urlPreview = useMemo(
    () => joinBaseUrlAndPath(connectorBaseUrl, form.path),
    [connectorBaseUrl, form.path],
  );

  function buildRequestConfig() {
    const rc = {
      auth: form.useConnectorAuth ? { mode: "connector" } : { mode: "none" },
      headers: pairsToRecord(form.headers),
      query_params: pairsToRecord(form.queryParams),
    };
    if (hasBody) {
      rc.content_type = form.contentType;
      rc.body_params = pairsToRecord(form.bodyParams);
    }
    const t = form.timeoutSec?.trim();
    if (t !== undefined && t !== "") {
      const n = Number(t);
      if (!Number.isFinite(n) || n < 1) {
        throw new Error(
          "Timeout debe ser un número mayor o igual a 1 (segundos).",
        );
      }
      rc.timeout = Math.round(n);
    }
    return rc;
  }

  return (
    <form
      className="stack action-builder-form"
      onSubmit={(event) => {
        event.preventDefault();
        let request_config;
        try {
          request_config = buildRequestConfig();
        } catch (err) {
          window.alert(err?.message || String(err));
          return;
        }
        onSubmit({
          name: form.name,
          method: form.method,
          path: form.path,
          request_config,
          input_schema_json: buildSchemaFromFields(form.schemaFields),
          input_schema_version: Number(form.inputSchemaVersion || 1),
          tag_ids: form.tag_ids,
        });
      }}
    >
      {(connectorBaseUrl || connectorAuthSummary) && (
        <div className="action-inherit-hint panel subtle">
          <strong className="text-sm">Qué aporta el conector</strong>
          <ul className="muted text-sm action-inherit-list">
            {connectorBaseUrl ? (
              <li>
                URL base: <code>{connectorBaseUrl}</code>
              </li>
            ) : null}
            {connectorAuthSummary ? (
              <li>Autenticación: {connectorAuthSummary}</li>
            ) : null}
          </ul>
        </div>
      )}

      <div className="action-builder-step">
        <span className="action-builder-step-label">1. Identificación</span>
        <div className="grid-2">
          <label className="field">
            Nombre visible
            <input
              required
              value={form.name}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, name: event.target.value }))
              }
              placeholder="Buscar cliente en CRM"
            />
          </label>
          <label className="field">
            Método HTTP
            <select
              value={form.method}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, method: event.target.value }))
              }
            >
              {METHODS.map((method) => (
                <option key={method} value={method}>
                  {method}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="action-builder-step">
        <span className="action-builder-step-label">2. Endpoint HTTP</span>
        <div className="grid-2">
          <label className="field">
            Path del endpoint
            <input
              required
              value={form.path}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, path: event.target.value }))
              }
              placeholder="/v1/customers/{id}"
            />
          </label>
          {hasBody ? (
            <label className="field">
              Content-Type (cuerpo)
              <select
                value={form.contentType}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    contentType: event.target.value,
                  }))
                }
              >
                <option value="application/json">application/json</option>
                <option value="application/x-www-form-urlencoded">
                  application/x-www-form-urlencoded
                </option>
                <option value="multipart/form-data">multipart/form-data</option>
                <option value="text/plain">text/plain</option>
              </select>
            </label>
          ) : (
            <div className="field">
              <span>Content-Type</span>
              <p className="muted text-sm">
                No aplica: el método {form.method} no envía cuerpo en esta
                configuración.
              </p>
            </div>
          )}
        </div>
        <p className="muted text-sm url-preview-line">
          Vista previa URL: <code>{urlPreview}</code>
        </p>
      </div>

      <div className="action-builder-step">
        <span className="action-builder-step-label">3. Petición HTTP</span>
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.useConnectorAuth}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                useConnectorAuth: event.target.checked,
              }))
            }
          />
          Incluir en la petición la autenticación definida en el conector
        </label>
        <p className="muted text-sm">
          Si lo desmarcas, la llamada no usará credenciales del conector (solo
          las cabeceras y params que indiques aquí).
        </p>

        <label className="field field-compact-top">
          Timeout opcional (segundos)
          <input
            type="number"
            min={1}
            step={1}
            value={form.timeoutSec}
            placeholder="p. ej. 30"
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                timeoutSec: event.target.value,
              }))
            }
          />
        </label>

        <KeyValueListEditor
          label="Headers"
          helperText="Cabeceras adicionales enviadas en la petición."
          rows={form.headers}
          onChange={(next) => setForm((prev) => ({ ...prev, headers: next }))}
        />
        <KeyValueListEditor
          label="Query params"
          helperText="Parámetros en la URL (?key=value)."
          rows={form.queryParams}
          onChange={(next) =>
            setForm((prev) => ({ ...prev, queryParams: next }))
          }
        />
        {hasBody ? (
          <KeyValueListEditor
            label="Body params"
            helperText="Plantillas por clave; solo con POST, PUT o PATCH."
            rows={form.bodyParams}
            onChange={(next) =>
              setForm((prev) => ({ ...prev, bodyParams: next }))
            }
          />
        ) : (
          <p className="muted text-sm">
            Los métodos {form.method} no usan cuerpo en este configurador. Usa
            query params o segmentos en el path.
          </p>
        )}
      </div>

      <details className="action-builder-details" open>
        <summary className="action-builder-details-summary">
          Schema de entrada (campos desde el chat)
        </summary>
        <div className="action-builder-step action-builder-step-nested">
          <div className="panel subtle">
            <div className="row spread">
              <strong>Schema de entrada</strong>
              <button
                type="button"
                onClick={() =>
                  setForm((prev) => ({
                    ...prev,
                    schemaFields: [
                      ...ensureSchemaRows(prev.schemaFields),
                      { name: "", type: "string" },
                    ],
                  }))
                }
              >
                Añadir campo
              </button>
            </div>
            <small className="muted">
              Define los campos que recibirá la acción desde el chat.
            </small>
            <div className="stack dense">
              {ensureSchemaRows(form.schemaFields).map((field, index) => (
                <div className="schema-row" key={`${field.name}-${index}`}>
                  <input
                    placeholder="Nombre"
                    value={field.name ?? ""}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        schemaFields: prev.schemaFields.map((item, current) =>
                          current === index
                            ? { ...item, name: event.target.value }
                            : item,
                        ),
                      }))
                    }
                  />
                  <select
                    value={field.type || "string"}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        schemaFields: prev.schemaFields.map((item, current) =>
                          current === index
                            ? { ...item, type: event.target.value }
                            : item,
                        ),
                      }))
                    }
                  >
                    {FIELD_TYPES.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                  <input
                    placeholder="Descripcion"
                    value={field.description ?? ""}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        schemaFields: prev.schemaFields.map((item, current) =>
                          current === index
                            ? { ...item, description: event.target.value }
                            : item,
                        ),
                      }))
                    }
                  />
                  <label className="check-row">
                    <input
                      type="checkbox"
                      checked={Boolean(field.required)}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          schemaFields: prev.schemaFields.map(
                            (item, current) =>
                              current === index
                                ? { ...item, required: event.target.checked }
                                : item,
                          ),
                        }))
                      }
                    />
                    Requerido
                  </label>
                  <button
                    type="button"
                    onClick={() =>
                      setForm((prev) => ({
                        ...prev,
                        schemaFields:
                          prev.schemaFields.length === 1
                            ? [{ name: "", type: "string" }]
                            : prev.schemaFields.filter(
                                (_, current) => current !== index,
                              ),
                      }))
                    }
                  >
                    Quitar
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </details>

      <details className="action-builder-details" open>
        <summary className="action-builder-details-summary">
          Tags y versión
        </summary>
        <div className="action-builder-step action-builder-step-nested">
          <div className="field">
            <span>Tags</span>
            <TagPicker
              options={tags}
              value={form.tag_ids}
              onChange={(next) =>
                setForm((prev) => ({ ...prev, tag_ids: next }))
              }
              onCreateTag={onCreateTag}
            />
          </div>

          <label className="field field-sm">
            Versión de schema
            <input
              type="number"
              value={form.inputSchemaVersion}
              min={1}
              onChange={(event) =>
                setForm((prev) => ({
                  ...prev,
                  inputSchemaVersion: Number(event.target.value || 1),
                }))
              }
            />
          </label>
        </div>
      </details>

      <div className="row">
        <button className="primary" type="submit" disabled={saving}>
          {saving
            ? "Guardando..."
            : initialAction
              ? "Guardar cambios"
              : "Crear acción"}
        </button>
        {initialAction ? (
          <button type="button" onClick={onCancel}>
            Cancelar
          </button>
        ) : null}
      </div>
    </form>
  );
}
