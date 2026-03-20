import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";
import { api } from "../../shared/apiClient";
import { ApiErrorBanner, LoadingBlock } from "../../shared/ui";
import { PreferencesPanel } from "../preferences/PreferencesPanel";

function initialValueByType(type) {
  if (type === "boolean") return false;
  return "";
}

function normalizeFields(schema) {
  return Array.isArray(schema?.fields) ? schema.fields : [];
}

function castValueByType(type, value) {
  if (type === "number") return Number(value);
  if (type === "boolean") return Boolean(value);
  return value;
}

function FieldRenderer({ field, value, onChange }) {
  const options = field.options || [];
  switch (field.type) {
    case "textarea":
      return <textarea rows={4} value={value} onChange={(e) => onChange(e.target.value)} />;
    case "number":
      return <input type="number" value={value} onChange={(e) => onChange(e.target.value)} />;
    case "boolean":
      return (
        <input type="checkbox" checked={Boolean(value)} onChange={(e) => onChange(e.target.checked)} />
      );
    case "select":
      return (
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">--</option>
          {options.map((opt) => (
            <option key={String(opt.value ?? opt)} value={String(opt.value ?? opt)}>
              {opt.label ?? opt.value ?? opt}
            </option>
          ))}
        </select>
      );
    case "radio":
      return (
        <div className="row">
          {options.map((opt) => {
            const optionValue = String(opt.value ?? opt);
            return (
              <label key={optionValue}>
                <input
                  type="radio"
                  name={field.name}
                  checked={String(value) === optionValue}
                  onChange={() => onChange(optionValue)}
                />
                {opt.label ?? opt.value ?? opt}
              </label>
            );
          })}
        </div>
      );
    case "date":
      return <input type="date" value={value} onChange={(e) => onChange(e.target.value)} />;
    default:
      return <input type="text" value={value} onChange={(e) => onChange(e.target.value)} />;
  }
}

export function ChatPage() {
  const [actionId, setActionId] = useState("");
  const [schema, setSchema] = useState(null);
  const [payload, setPayload] = useState({});
  const [result, setResult] = useState(null);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const fields = useMemo(() => normalizeFields(schema?.input_schema_json), [schema]);

  async function loadSchema(event) {
    event.preventDefault();
    setLoadingSchema(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.get(`/actions/${actionId}/input-schema`);
      setSchema(data);
      const defaults = {};
      for (const field of normalizeFields(data?.input_schema_json)) {
        defaults[field.name] = initialValueByType(field.type);
      }
      setPayload(defaults);
    } catch (nextError) {
      setError(nextError);
      setSchema(null);
    } finally {
      setLoadingSchema(false);
    }
  }

  async function executeAction(event) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const payloadObject = {};
      for (const field of fields) {
        payloadObject[field.name] = castValueByType(field.type, payload[field.name]);
      }
      const execution = await api.post(`/actions/${actionId}/execute`, { payload: payloadObject });
      setResult(execution);
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="content">
      <section className="panel">
        <div className="page-header">
          <div>
            <h1>Chat MVP</h1>
            <small>
              Usuario: {user?.sub} ({user?.role})
            </small>
          </div>
          <div className="row">
            {isAdmin ? (
              <button onClick={() => navigate("/admin/users")}>Ir a admin</button>
            ) : null}
            <button
              onClick={async () => {
                await logout();
                navigate("/login");
              }}
            >
              Logout
            </button>
          </div>
        </div>
        <ApiErrorBanner error={error} />
        <form className="row" onSubmit={loadSchema}>
          <label className="field">
            action_id
            <input
              aria-label="action_id"
              value={actionId}
              onChange={(event) => setActionId(event.target.value)}
              required
            />
          </label>
          <button className="primary" type="submit" disabled={loadingSchema || !actionId}>
            {loadingSchema ? "Cargando schema..." : "Cargar schema"}
          </button>
        </form>
      </section>

      {loadingSchema ? <LoadingBlock /> : null}

      {schema ? (
        <section className="panel">
          <h2>Formulario dinámico ({schema.input_schema_version || "v1"})</h2>
          <form className="stack" onSubmit={executeAction}>
            {fields.map((field) => (
              <label key={field.name} className="field">
                {field.label || field.name}
                <FieldRenderer
                  field={field}
                  value={payload[field.name] ?? ""}
                  onChange={(next) => setPayload((prev) => ({ ...prev, [field.name]: next }))}
                />
              </label>
            ))}
            <button className="primary" type="submit" disabled={submitting}>
              {submitting ? "Ejecutando..." : "Ejecutar acción"}
            </button>
          </form>
        </section>
      ) : null}

      {result ? (
        <section className="panel">
          <h2>Resultado</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </section>
      ) : null}

      <PreferencesPanel />
    </div>
  );
}
