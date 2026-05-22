/** Apply theme to document root (system = no data-theme, uses CSS default). */
export function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "dark") {
    root.setAttribute("data-theme", "dark");
    return;
  }
  if (theme === "light") {
    root.setAttribute("data-theme", "light");
    return;
  }
  root.removeAttribute("data-theme");
}
