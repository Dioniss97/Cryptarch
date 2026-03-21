import { Navigate, useParams } from "react-router-dom";
import { CrudPage } from "./CrudPage";
import { RESOURCE_CONFIGS } from "./resourceConfigs";

export function AdminResourcePage({ resource: resourceProp }) {
  const { resource: resourceParam } = useParams();
  const resource = resourceProp ?? resourceParam;
  if (resource === "actions")
    return <Navigate to="/admin/connectors" replace />;
  if (resource === "users") return <Navigate to="/admin/users" replace />;
  if (resource === "connectors")
    return <Navigate to="/admin/connectors" replace />;
  if (resource === "documents")
    return <Navigate to="/admin/documents" replace />;
  const config = RESOURCE_CONFIGS[resource];
  if (!config) return <Navigate to="/admin/users" replace />;
  return <CrudPage config={config} />;
}
