"""
Contrato de dominio compartido con packages/shared/data/domain.json.

Se carga una vez al importar el módulo (coste trivial). No requiere Node.
Si falta el fichero (p. ej. despliegue parcial), la API no arranca: clone el monorepo completo.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Final

__all__ = [
    "ROLE_ADMIN",
    "ROLE_USER",
    "DOCUMENT_STATUS_QUEUED",
    "DOCUMENT_STATUS_PROCESSING",
    "DOCUMENT_STATUS_INDEXED",
    "DOCUMENT_STATUS_ERROR",
    "SAVED_FILTER_TARGET_USER",
    "SAVED_FILTER_TARGET_ACTION",
    "SAVED_FILTER_TARGET_DOCUMENT",
    "TOKEN_TYPE_BEARER",
    "SESSION_STORAGE_KEY",
    "USER_THEME_SYSTEM",
    "USER_THEME_LIGHT",
    "USER_THEME_DARK",
    "UserRole",
    "SavedFilterTarget",
    "DocumentStatus",
    "UserTheme",
]


def _repo_root() -> Path:
    # apps/api/shared_contract.py -> parent=apps/api, parent.parent=apps, parent.parent.parent=repo root
    return Path(__file__).resolve().parent.parent.parent


def _load_domain() -> dict:
    path = _repo_root() / "packages" / "shared" / "data" / "domain.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing shared domain contract at {path}. "
            "Use the full monorepo so packages/shared exists."
        )
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("domain.json must be a JSON object")
    return data


_DATA = _load_domain()


def _expect_set(key: str, expected: set[str]) -> None:
    raw = _DATA.get(key)
    if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
        raise ValueError(f"domain.json[{key!r}] must be a list of strings")
    got = frozenset(raw)
    if got != expected:
        raise RuntimeError(
            f"domain.json[{key!r}] mismatch: expected {sorted(expected)}, got {sorted(got)}"
        )


_expect_set("roles", {"admin", "user"})
_expect_set("document_status", {"queued", "processing", "indexed", "error"})
_expect_set("saved_filter_target", {"user", "action", "document"})
_expect_set("user_theme", {"system", "light", "dark"})

ROLE_ADMIN: Final[str] = "admin"
ROLE_USER: Final[str] = "user"

DOCUMENT_STATUS_QUEUED: Final[str] = "queued"
DOCUMENT_STATUS_PROCESSING: Final[str] = "processing"
DOCUMENT_STATUS_INDEXED: Final[str] = "indexed"
DOCUMENT_STATUS_ERROR: Final[str] = "error"

SAVED_FILTER_TARGET_USER: Final[str] = "user"
SAVED_FILTER_TARGET_ACTION: Final[str] = "action"
SAVED_FILTER_TARGET_DOCUMENT: Final[str] = "document"

USER_THEME_SYSTEM: Final[str] = "system"
USER_THEME_LIGHT: Final[str] = "light"
USER_THEME_DARK: Final[str] = "dark"

_token = _DATA.get("token_type_bearer")
if not isinstance(_token, str) or _token != "bearer":
    raise RuntimeError('domain.json token_type_bearer must be the string "bearer"')
TOKEN_TYPE_BEARER: Final[str] = _token

_session_key = _DATA.get("session_storage_key")
if not isinstance(_session_key, str) or not _session_key:
    raise RuntimeError("domain.json session_storage_key must be a non-empty string")
SESSION_STORAGE_KEY: Final[str] = _session_key


def _enum_values_match(enum_cls: type[Enum], expected: set[str]) -> None:
    got = {m.value for m in enum_cls}
    if got != expected:
        raise RuntimeError(
            f"{enum_cls.__name__} values {got} != domain.json {expected}"
        )


class UserRole(str, Enum):
    admin = ROLE_ADMIN
    user = ROLE_USER


class SavedFilterTarget(str, Enum):
    user = SAVED_FILTER_TARGET_USER
    action = SAVED_FILTER_TARGET_ACTION
    document = SAVED_FILTER_TARGET_DOCUMENT


class DocumentStatus(str, Enum):
    queued = DOCUMENT_STATUS_QUEUED
    processing = DOCUMENT_STATUS_PROCESSING
    indexed = DOCUMENT_STATUS_INDEXED
    error = DOCUMENT_STATUS_ERROR


class UserTheme(str, Enum):
    system = USER_THEME_SYSTEM
    light = USER_THEME_LIGHT
    dark = USER_THEME_DARK


_enum_values_match(UserRole, {ROLE_ADMIN, ROLE_USER})
_enum_values_match(
    SavedFilterTarget,
    {
        SAVED_FILTER_TARGET_USER,
        SAVED_FILTER_TARGET_ACTION,
        SAVED_FILTER_TARGET_DOCUMENT,
    },
)
_enum_values_match(
    DocumentStatus,
    {
        DOCUMENT_STATUS_QUEUED,
        DOCUMENT_STATUS_PROCESSING,
        DOCUMENT_STATUS_INDEXED,
        DOCUMENT_STATUS_ERROR,
    },
)
_enum_values_match(UserTheme, {USER_THEME_SYSTEM, USER_THEME_LIGHT, USER_THEME_DARK})
