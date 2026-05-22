import { test, expect } from "@playwright/test";

const DEV_TENANT = "00000000-0000-4000-8000-000000000001";
const DEV_EMAIL = "admin@dev.local";
const DEV_PASSWORD = "admin";

async function devLogin(page) {
  await page.goto("/login");
  await page.getByLabel("Tenant ID").fill(DEV_TENANT);
  await page.getByLabel("Email").fill(DEV_EMAIL);
  await page.getByLabel("Password").fill(DEV_PASSWORD);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/admin\/users/);
}

test("admin login reaches users workspace", async ({ page }) => {
  await devLogin(page);
  await expect(page.getByRole("heading", { name: "Usuarios" })).toBeVisible();
});

test("admin navigates to connectors", async ({ page }) => {
  await devLogin(page);
  await page.getByRole("link", { name: /Conectores/i }).click();
  await expect(page).toHaveURL(/\/admin\/connectors/);
});

test("chat assistant page loads after login", async ({ page }) => {
  await devLogin(page);
  await page.getByRole("link", { name: /Chat/i }).click();
  await expect(page).toHaveURL(/\/chat/);
  await expect(page.getByRole("heading", { name: "Asistente" })).toBeVisible();
});
