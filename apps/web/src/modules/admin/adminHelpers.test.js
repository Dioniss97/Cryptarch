import { describe, expect, it } from "vitest";
import {
  buildAuthConfigFromConnectorForm,
  chatFieldsFromInputSchemaJson,
  emptyConnectorAuthFormFields,
  joinBaseUrlAndPath,
  parseConnectorAuthForForm,
} from "./adminHelpers";

describe("joinBaseUrlAndPath", () => {
  it("une base y path relativo", () => {
    expect(joinBaseUrlAndPath("https://api.example.com/", "/v1/x")).toBe(
      "https://api.example.com/v1/x",
    );
  });

  it("acepta path sin slash inicial", () => {
    expect(joinBaseUrlAndPath("https://api.example.com", "v1/x")).toBe(
      "https://api.example.com/v1/x",
    );
  });

  it("devuelve URL absoluta en path sin tocar", () => {
    expect(joinBaseUrlAndPath("https://a.com", "https://other/full")).toBe(
      "https://other/full",
    );
  });
});

describe("chatFieldsFromInputSchemaJson", () => {
  it("convierte JSON Schema del admin a campos de UI", () => {
    const schema = {
      type: "object",
      required: ["title"],
      properties: {
        title: { type: "string", description: "Título" },
        count: { type: "integer" },
        done: { type: "boolean" },
      },
    };
    const fields = chatFieldsFromInputSchemaJson(schema);
    expect(fields).toHaveLength(3);
    expect(fields[0]).toMatchObject({
      name: "title",
      type: "text",
      label: "title",
      description: "Título",
      required: true,
    });
    expect(fields[1]).toMatchObject({
      name: "count",
      type: "number",
      required: false,
    });
    expect(fields[2]).toMatchObject({
      name: "done",
      type: "boolean",
      required: false,
    });
  });

  it("usa enum como select y title como label", () => {
    const schema = {
      type: "object",
      properties: {
        size: {
          type: "string",
          title: "Tamaño",
          enum: ["S", "M"],
        },
      },
    };
    const [field] = chatFieldsFromInputSchemaJson(schema);
    expect(field.type).toBe("select");
    expect(field.label).toBe("Tamaño");
    expect(field.options).toEqual([
      { value: "S", label: "S" },
      { value: "M", label: "M" },
    ]);
  });

  it("acepta formato textarea vía format o x-ui-widget", () => {
    expect(
      chatFieldsFromInputSchemaJson({
        type: "object",
        properties: { notes: { type: "string", format: "textarea" } },
      })[0].type,
    ).toBe("textarea");
    expect(
      chatFieldsFromInputSchemaJson({
        type: "object",
        properties: { notes: { type: "string", "x-ui-widget": "textarea" } },
      })[0].type,
    ).toBe("textarea");
  });

  it("retrocompatibilidad: wrapper legacy fields[]", () => {
    const fields = chatFieldsFromInputSchemaJson({
      fields: [
        {
          name: "a",
          type: "number",
          label: "A",
          required: true,
        },
      ],
    });
    expect(fields[0]).toMatchObject({ name: "a", type: "number", label: "A" });
  });
});

describe("connector auth form", () => {
  it("redondea trip bearer + token_env", () => {
    const fields = {
      base_url: "x",
      ...emptyConnectorAuthFormFields(),
      authKind: "bearer",
      authBearerTokenEnv: "T",
    };
    const api = buildAuthConfigFromConnectorForm(fields);
    const again = parseConnectorAuthForForm(api);
    expect(api).toEqual({ type: "bearer", token_env: "T" });
    expect(again.authKind).toBe("bearer");
    expect(again.authBearerTokenEnv).toBe("T");
  });

  it("redondea trip basic auth guiado", () => {
    const fields = {
      base_url: "x",
      ...emptyConnectorAuthFormFields(),
      authKind: "basic",
      authBasicUsername: "bot",
      authBasicPasswordEnv: "CRM_BASIC_PASSWORD",
    };
    const api = buildAuthConfigFromConnectorForm(fields);
    const again = parseConnectorAuthForForm(api);
    expect(api).toEqual({
      type: "basic",
      username: "bot",
      password_env: "CRM_BASIC_PASSWORD",
    });
    expect(again.authKind).toBe("basic");
    expect(again.authBasicUsername).toBe("bot");
    expect(again.authBasicPasswordEnv).toBe("CRM_BASIC_PASSWORD");
  });

  it("redondea trip oauth2 guiado con client credentials", () => {
    const fields = {
      base_url: "x",
      ...emptyConnectorAuthFormFields(),
      authKind: "oauth2",
      authOAuth2ClientId: "crm-client",
      authOAuth2ClientSecretEnv: "CRM_CLIENT_SECRET",
      authOAuth2TokenUrl: "https://auth.example.com/oauth/token",
      authOAuth2Scope: "contacts.read contacts.write",
    };
    const api = buildAuthConfigFromConnectorForm(fields);
    const again = parseConnectorAuthForForm(api);
    expect(api).toEqual({
      type: "oauth2",
      grant_type: "client_credentials",
      client_id: "crm-client",
      client_secret_env: "CRM_CLIENT_SECRET",
      token_url: "https://auth.example.com/oauth/token",
      scope: "contacts.read contacts.write",
    });
    expect(again.authKind).toBe("oauth2");
    expect(again.authOAuth2ClientId).toBe("crm-client");
    expect(again.authOAuth2ClientSecretEnv).toBe("CRM_CLIENT_SECRET");
    expect(again.authOAuth2TokenUrl).toBe(
      "https://auth.example.com/oauth/token",
    );
    expect(again.authOAuth2Scope).toBe("contacts.read contacts.write");
  });

  it("acepta scopes legacy en array al abrir el formulario", () => {
    const again = parseConnectorAuthForForm({
      type: "oauth2",
      client_id: "crm-client",
      scopes: ["contacts.read", "contacts.write"],
    });
    expect(again.authKind).toBe("oauth2");
    expect(again.authOAuth2Scope).toBe("contacts.read contacts.write");
  });
});
