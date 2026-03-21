import { Navigate } from "react-router-dom";
import { PublicOnly, RequireAdmin, RequireAuth } from "./guards";
import { LoginPage } from "../modules/auth/LoginPage";
import { AdminLayout } from "../modules/admin/AdminLayout";
import { AdminResourcePage } from "../modules/admin/AdminResourcePage";
import { ChatPage } from "../modules/chat/ChatPage";
import { UsersWorkspace } from "../modules/admin/UsersWorkspace";
import { ConnectorsWorkspace } from "../modules/admin/ConnectorsWorkspace";
import { DocumentsLibraryPage } from "../modules/admin/DocumentsLibraryPage";

export const appRoutes = [
  {
    path: "/",
    element: <Navigate to="/chat" replace />,
  },
  {
    path: "/login",
    element: (
      <PublicOnly>
        <LoginPage />
      </PublicOnly>
    ),
  },
  {
    element: <RequireAuth />,
    children: [
      { path: "/chat", element: <ChatPage /> },
      {
        element: <RequireAdmin />,
        children: [
          {
            path: "/admin",
            element: <AdminLayout />,
            children: [
              { index: true, element: <Navigate to="/admin/users" replace /> },
              { path: "users", element: <UsersWorkspace /> },
              { path: "connectors", element: <ConnectorsWorkspace /> },
              { path: "documents", element: <DocumentsLibraryPage /> },
              { path: "tags", element: <AdminResourcePage resource="tags" /> },
              {
                path: "filters",
                element: <AdminResourcePage resource="filters" />,
              },
              {
                path: "groups",
                element: <AdminResourcePage resource="groups" />,
              },
              { path: ":resource", element: <AdminResourcePage /> },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/chat" replace />,
  },
];
