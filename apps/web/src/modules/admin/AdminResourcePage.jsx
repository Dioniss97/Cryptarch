import { Navigate, useParams } from "react-router-dom";
import { CrudPage } from "./CrudPage";
import { RESOURCE_CONFIGS } from "./resourceConfigs";

export function AdminResourcePage() {
  const { resource } = useParams();
  const config = RESOURCE_CONFIGS[resource];
  if (!config) return <Navigate to="/admin/users" replace />;
  return <CrudPage config={config} />;
}
