import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthProvider";
import { api } from "../../shared/apiClient";
import { ApiErrorBanner, EmptyState, LoadingBlock } from "../../shared/ui";
import { ProfileMenu } from "../admin/ProfileMenu";
import { ActionExecutionResult } from "./ActionExecutionResult";
import { AllowedActionsList } from "./AllowedActionsList";
import {
  buildInitialPayload,
  buildExecutePayload,
  DynamicActionForm,
} from "./DynamicActionForm";

export function ChatPage() {
  const [actions, setActions] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [selectedAction, setSelectedAction] = useState(null);
  const [payload, setPayload] = useState({});
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();

  const loadActions = useCallback(async () => {
    setLoadingList(true);
    setError(null);
    try {
      const data = await api.get("/actions");
      setActions(Array.isArray(data) ? data : []);
    } catch (nextError) {
      setError(nextError);
      setActions([]);
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    loadActions();
  }, [loadActions]);

  function selectAction(action) {
    setSelectedAction(action);
    setResult(null);
    setError(null);
    const { defaults } = buildInitialPayload(action?.input_schema_json);
    setPayload(defaults);
  }

  async function executeAction() {
    if (!selectedAction?.id) return;
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const payloadObject = buildExecutePayload(
        selectedAction.input_schema_json,
        payload,
      );
      const execution = await api.post(
        `/actions/${selectedAction.id}/execute`,
        { payload: payloadObject },
      );
      setResult(execution);
    } catch (nextError) {
      const st = nextError?.status;
      if (st === 404 || st === 501) {
        setError({
          status: st,
          message:
            "La ejecución de acciones aún no está disponible. Disponible próximamente (task-08g-bis).",
        });
      } else {
        setError(nextError);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="content">
      <section className="panel">
        <div className="page-header">
          <div>
            <h1>Asistente</h1>
            <small>
              Usuario: {user?.sub} ({user?.role})
            </small>
          </div>
          <div className="row page-header-actions">
            {isAdmin ? (
              <button type="button" onClick={() => navigate("/admin/users")}>
                Ir a admin
              </button>
            ) : null}
            <ProfileMenu />
          </div>
        </div>
        <ApiErrorBanner error={error} />
        <p className="text-sm muted" style={{ marginTop: 0 }}>
          Elige una acción para rellenar el formulario y ejecutarla.
        </p>
      </section>

      {loadingList ? <LoadingBlock label="Cargando acciones…" /> : null}

      {!loadingList && !error && actions.length === 0 ? (
        <EmptyState
          title="No hay acciones disponibles"
          description="Cuando existan acciones en tu espacio, aparecerán aquí para ejecutarlas."
        />
      ) : null}

      {!loadingList && !error && actions.length > 0 ? (
        <div className="chat-workspace">
          <section className="panel">
            <h2 style={{ marginTop: 0, fontSize: "1.05rem" }}>Acciones</h2>
            <AllowedActionsList
              actions={actions}
              selectedId={selectedAction?.id}
              onSelect={selectAction}
            />
          </section>

          <section className="panel">
            {selectedAction ? (
              <>
                <h2 style={{ marginTop: 0, fontSize: "1.15rem" }}>
                  {selectedAction.name?.trim() || "Acción sin nombre"}
                </h2>
                <DynamicActionForm
                  schemaJson={selectedAction.input_schema_json}
                  schemaVersion={selectedAction.input_schema_version}
                  payload={payload}
                  onPayloadChange={setPayload}
                  onSubmit={executeAction}
                  submitting={submitting}
                  submitLabel="Ejecutar"
                />
                <ActionExecutionResult result={result} />
              </>
            ) : (
              <EmptyState
                title="Selecciona una acción"
                description="Pulsa una acción de la lista para ver el formulario y ejecutarla."
              />
            )}
          </section>
        </div>
      ) : null}
    </div>
  );
}
