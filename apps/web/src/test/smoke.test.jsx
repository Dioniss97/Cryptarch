import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../app/AuthProvider";
import { appRoutes } from "../app/router";

function renderWithRoute(route) {
  const router = createMemoryRouter(appRoutes, { initialEntries: [route] });
  return render(
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>,
  );
}

function mockJsonResponse(status, payload) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    text: () => Promise.resolve(payload ? JSON.stringify(payload) : ""),
  });
}

describe("smoke routes", () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn();
  });

  it("redirige admin sin sesión a login y permite login hacia admin", async () => {
    fetch
      .mockImplementationOnce(() =>
        mockJsonResponse(200, { access_token: "token-demo", token_type: "bearer" }),
      )
      .mockImplementationOnce(() =>
        mockJsonResponse(200, { sub: "admin@test", tenant_id: "t1", role: "admin" }),
      )
      .mockImplementationOnce(() => mockJsonResponse(200, []));

    renderWithRoute("/admin/users");
    expect(await screen.findByRole("heading", { name: "Acceso" })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Tenant ID"), { target: { value: "t1" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "admin@test" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "secret" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Users" })).toBeInTheDocument();
    });
  });

  it("renderiza chat para usuario autenticado", async () => {
    localStorage.setItem(
      "cryptarch_session",
      JSON.stringify({
        token: "token-user",
        user: { sub: "user@test", tenant_id: "t1", role: "user" },
      }),
    );
    fetch.mockImplementation(() => mockJsonResponse(200, { theme: "system", metadata: {} }));

    renderWithRoute("/chat");
    expect(await screen.findByRole("heading", { name: "Chat MVP" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Preferencias" })).toBeInTheDocument();
  });
});
