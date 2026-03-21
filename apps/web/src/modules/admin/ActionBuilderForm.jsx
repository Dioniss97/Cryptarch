import { useMemo, useState } from "react";
import { TagPicker } from "./TagPicker";
import { KeyValueListEditor } from "./KeyValueListEditor";
import {
  buildSchemaFromFields,
  extractSchemaFields,
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
  return {
    name: initialAction?.name || "",
    method: (initialAction?.method || "POST").toUpperCase(),
    path: initialAction?.path || "",
    contentType: requestConfig?.content_type || "application/json",
    useConnectorAuth: requestConfig?.auth?.mode !== "none",
    headers: recordToPairs(requestConfig?.headers),
    queryParams: recordToPairs(requestConfig?.query_params),
    bodyParams: recordToPairs(requestConfig?.body_params),
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
  tags,
  saving,
  onSubmit,
  onCancel,
  onCreateTag,
}) {
  const [form, setForm] = useState(() => initialState(initialAction));
  const hasBody = useMemo(
    () =>
      ["POST", "PUT", "PATCH"].includes(
        String(form.method || "").toUpperCase(),
      ),
    [form.method],
  );

  return (
    <form
      className="stack action-builder-form"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit({
          name: form.name,
          method: form.method,
          path: form.path,
          request_config: {
            content_type: form.contentType,
            auth: form.useConnectorAuth
              ? { mode: "connector" }
              : { mode: "none" },
            headers: pairsToRecord(form.headers),
            query_params: pairsToRecord(form.queryParams),
            ...(hasBody ? { body_params: pairsToRecord(form.bodyParams) } : {}),
          },
          input_schema_json: buildSchemaFromFields(form.schemaFields),
          input_schema_version: Number(form.inputSchemaVersion || 1),
          tag_ids: form.tag_ids,
        });
      }}
    >
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
          <label className="field">
            Content-Type
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
        </div>
      </div>

      <div className="action-builder-step">
        <span className="action-builder-step-label">3. Parámetros</span>
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
          Reutilizar autenticación del conector
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
            helperText="Solo para métodos POST, PUT, PATCH."
            rows={form.bodyParams}
            onChange={(next) =>
              setForm((prev) => ({ ...prev, bodyParams: next }))
            }
          />
        ) : (
          <small className="muted">
            GET no envía body. Usa query params o path.
          </small>
        )}
      </div>

      <div className="action-builder-step">
        <span className="action-builder-step-label">4. Schema de entrada</span>
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
                        schemaFields: prev.schemaFields.map((item, current) =>
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

      <div className="action-builder-step">
        <span className="action-builder-step-label">5. Metadata</span>
        <div className="field">
          <span>Tags</span>
          <TagPicker
            options={tags}
            value={form.tag_ids}
            onChange={(next) => setForm((prev) => ({ ...prev, tag_ids: next }))}
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
