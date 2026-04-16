const AUTH_KIND_OPTIONS = [
  {
    value: "none",
    title: "Sin auth",
    description: "El conector no añade credenciales por defecto.",
  },
  {
    value: "bearer",
    title: "Bearer",
    description: "Usa un token desde una variable de entorno.",
  },
  {
    value: "api_key",
    title: "API key",
    description: "Envía una clave en una cabecera HTTP.",
  },
  {
    value: "basic",
    title: "Basic Auth",
    description: "Guarda usuario y referencia al secreto de password.",
  },
  {
    value: "oauth2",
    title: "OAuth2",
    description: "Configura client credentials de forma guiada.",
  },
  {
    value: "custom",
    title: "JSON avanzado",
    description: "Escape hatch para configuraciones no guiadas.",
  },
];

export function AuthKindSelector({ value, onChange }) {
  return (
    <div
      className="auth-kind-selector"
      role="radiogroup"
      aria-label="Tipo de autenticación"
    >
      {AUTH_KIND_OPTIONS.map((option) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            className={`auth-kind-chip${selected ? " selected" : ""}`}
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
          >
            <strong>{option.title}</strong>
            <small>{option.description}</small>
          </button>
        );
      })}
    </div>
  );
}
