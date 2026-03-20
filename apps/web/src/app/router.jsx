import { Navigate } from "react-router-dom";
import { PublicOnly, RequireAdmin, RequireAuth } from "./guards";
import { LoginPage } from "../modules/auth/LoginPage";
import { AdminLayout } from "../modules/admin/AdminLayout";
import { AdminResourcePage } from "../modules/admin/AdminResourcePage";
import { ChatPage } from "../modules/chat/ChatPage";

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
