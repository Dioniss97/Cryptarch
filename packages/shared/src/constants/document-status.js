/**
 * Estados del ciclo de vida de un documento (ingesta / índice).
 * Alineado con comentarios en schemas y tests API.
 * @type {readonly ["queued", "processing", "indexed", "error"]}
 */
export const DOCUMENT_STATUSES = Object.freeze([
  "queued",
  "processing",
  "indexed",
  "error",
]);

export const DOCUMENT_STATUS_QUEUED = "queued";
export const DOCUMENT_STATUS_PROCESSING = "processing";
export const DOCUMENT_STATUS_INDEXED = "indexed";
export const DOCUMENT_STATUS_ERROR = "error";
