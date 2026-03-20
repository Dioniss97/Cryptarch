import { useEffect, useState } from "react";
import { api } from "../../shared/apiClient";
import { ApiErrorBanner, LoadingBlock } from "../../shared/ui";

const DEFAULTS = {
  theme: "system",
  language: "es",
  table_density: "comfortable",
  metadata: "{}",
};

export function PreferencesPanel() {
  const [form, setForm] = useState(DEFAULTS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [ok, setOk] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = (await api.get("/me/preferences")) || {};
        setForm({
          theme: data.theme || "system",
          language: data.language || "es",
          table_density: data.table_density || "comfortable",
          metadata: JSON.stringify(data.metadata || {}, null, 2),
        });
      } catch (nextError) {
        setError(nextError);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setOk("");
    try {
      await api.patch("/me/preferences", {
        theme: form.theme,
        language: form.language,
        table_density: form.table_density,
        metadata: JSON.parse(form.metadata || "{}"),
      });
      setOk("Preferencias guardadas.");
    } catch (nextError) {
      setError(nextError);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel">
      <h2>Preferencias</h2>
      {loading ? <LoadingBlock /> : null}
      <ApiErrorBanner error={error} />
      {ok ? <div className="badge success">{ok}</div> : null}
      {!loading ? (
        <form className="stack" onSubmit={onSubmit}>
          <label className="field">
            Theme
            <select
              value={form.theme}
              onChange={(event) => setForm((prev) => ({ ...prev, theme: event.target.value }))}
            >
              <option value="system">system</option>
              <option value="light">light</option>
              <option value="dark">dark</option>
            </select>
          </label>
          <label className="field">
            Language
            <input
              value={form.language}
              onChange={(event) => setForm((prev) => ({ ...prev, language: event.target.value }))}
            />
          </label>
          <label className="field">
            Table density
            <select
              value={form.table_density}
              onChange={(event) => setForm((prev) => ({ ...prev, table_density: event.target.value }))}
            >
              <option value="comfortable">comfortable</option>
              <option value="compact">compact</option>
            </select>
          </label>
          <label className="field">
            Metadata (JSON)
            <textarea
              rows={4}
              value={form.metadata}
              onChange={(event) => setForm((prev) => ({ ...prev, metadata: event.target.value }))}
            />
          </label>
          <button className="primary" type="submit" disabled={saving}>
            {saving ? "Guardando..." : "Guardar preferencias"}
          </button>
        </form>
      ) : null}
    </section>
  );
}
