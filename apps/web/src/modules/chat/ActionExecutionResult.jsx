import { useMemo, useState } from "react";
import { toJsonText } from "../admin/adminHelpers";

function isStructuredResult(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  return (
    Object.prototype.hasOwnProperty.call(value, "status") ||
    Object.prototype.hasOwnProperty.call(value, "message") ||
    Object.prototype.hasOwnProperty.call(value, "data")
  );
}

export function ActionExecutionResult({ result }) {
  const [showRaw, setShowRaw] = useState(false);
  const structured = useMemo(() => isStructuredResult(result), [result]);

  if (result === null || result === undefined) return null;

  const jsonText = toJsonText(result);

  return (
    <div className="stack dense">
      <div className="row spread">
        <h3 style={{ margin: 0 }}>Resultado</h3>
        <label className="check-row text-sm">
          <input
            type="checkbox"
            checked={showRaw}
            onChange={(e) => setShowRaw(e.target.checked)}
          />
          Ver JSON
        </label>
      </div>

      {showRaw ? (
        <pre
          className="chat-result-json"
          style={{
            margin: 0,
            padding: 12,
            background: "#f4f6fb",
            borderRadius: 8,
            overflow: "auto",
            fontSize: 13,
          }}
        >
          {jsonText}
        </pre>
      ) : structured ? (
        <div className="stack dense chat-result-structured">
          {Object.prototype.hasOwnProperty.call(result, "status") ? (
            <div>
              <strong className="text-sm">Estado</strong>
              <div>{String(result.status)}</div>
            </div>
          ) : null}
          {Object.prototype.hasOwnProperty.call(result, "message") ? (
            <div>
              <strong className="text-sm">Mensaje</strong>
              <div>{String(result.message)}</div>
            </div>
          ) : null}
          {Object.prototype.hasOwnProperty.call(result, "data") ? (
            <div>
              <strong className="text-sm">Datos</strong>
              <pre
                style={{
                  margin: "6px 0 0",
                  padding: 10,
                  background: "#f4f6fb",
                  borderRadius: 8,
                  overflow: "auto",
                  fontSize: 13,
                }}
              >
                {typeof result.data === "string"
                  ? result.data
                  : toJsonText(result.data)}
              </pre>
            </div>
          ) : null}
        </div>
      ) : (
        <pre
          style={{
            margin: 0,
            padding: 12,
            background: "#f4f6fb",
            borderRadius: 8,
            overflow: "auto",
            fontSize: 13,
          }}
        >
          {jsonText}
        </pre>
      )}
    </div>
  );
}
