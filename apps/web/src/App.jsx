import { RouterProvider, createBrowserRouter } from "react-router-dom";
import { AuthProvider } from "./app/AuthProvider";
import { appRoutes } from "./app/router";

const browserRouter = createBrowserRouter(appRoutes);

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={browserRouter} />
    </AuthProvider>
  );
}
