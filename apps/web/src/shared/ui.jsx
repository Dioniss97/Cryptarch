import { useState } from "react";

const STATUS_CLASS = {
  indexed: "badge success",
  processing: "badge warning",
  error: "badge danger",
  active: "badge success",
  inactive: "badge",
};

export function StatusBadge({ status = "unknown" }) {
  const key = String(status).toLowerCase();
  return <span className={STATUS_CLASS[key] || "badge"}>{String(status)}</span>;
}

export function ApiErrorBanner({ error }) {
  if (!error) return null;

  const statusMap = {
    401: "401 No autenticado",
    403: "403 Sin permisos",
    404: "404 No encontrado",
    409: "409 Conflicto",
    422: "422 Validación",
  };

  const title = statusMap[error.status] || `${error.status || "?"} Error`;
  return (
    <div className="error-banner" role="alert">
      <strong>{title}</strong>
      <div>{error.message || "Ha ocurrido un error"}</div>
      {error.code ? <small>Código: {error.code}</small> : null}
    </div>
  );
}

export function LoadingBlock({ label = "Cargando..." }) {
  return <div className="loading-block">{label}</div>;
}

export function EmptyState({ title = "Sin datos", description = "No hay elementos para mostrar." }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export function ConfirmDelete({ label = "Eliminar", onConfirm }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <span>
      <button
        className="danger"
        onClick={() => {
          setIsOpen(true);
        }}
      >
        {label}
      </button>
      {isOpen ? (
        <span className="inline-confirm">
          Confirmar?
          <button
            className="danger"
            onClick={() => {
              onConfirm();
              setIsOpen(false);
            }}
          >
            Si
          </button>
          <button onClick={() => setIsOpen(false)}>No</button>
        </span>
      ) : null}
    </span>
  );
}
