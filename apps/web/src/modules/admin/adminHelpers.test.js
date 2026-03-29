import { describe, expect, it } from "vitest";
import {
  buildAuthConfigFromConnectorForm,
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
    expect(
      joinBaseUrlAndPath("https://a.com", "https://other/full"),
    ).toBe("https://other/full");
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
});
