/**
 * Tipo de entidad a la que aplica un SavedFilter (dominio).
 * @type {readonly ["user", "action", "document"]}
 */
export const SAVED_FILTER_TARGET_TYPES = Object.freeze([
  "user",
  "action",
  "document",
]);

export const SAVED_FILTER_TARGET_USER = "user";
export const SAVED_FILTER_TARGET_ACTION = "action";
export const SAVED_FILTER_TARGET_DOCUMENT = "document";
