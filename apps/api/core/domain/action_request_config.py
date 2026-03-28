"""Request builder config for HTTP actions: shape validation and method/body rules."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

NO_REQUEST_BODY_METHODS = frozenset({"GET", "DELETE"})


class RequestConfigValidationError(ValueError):
    """request_config is not a valid request builder payload for the given method."""


class ActionRequestConfigPayload(BaseModel):
    """Known fields for the admin request builder; unknown keys are kept for backward compatibility."""

    model_config = ConfigDict(extra="allow")

    headers: dict[str, Any] | None = None
    query: dict[str, Any] | None = None
    body: Any | None = None


def validate_and_normalize_request_config(
    method: str,
    raw: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Parse request_config, enforce GET/DELETE have no body, return a normalized dict for persistence.

    Legacy blobs (e.g. only ``timeout``) remain valid as long as ``body`` is absent/None.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise RequestConfigValidationError("request_config must be a JSON object")

    m = (method or "").strip().upper()
    try:
        parsed = ActionRequestConfigPayload.model_validate(raw)
    except Exception as exc:
        raise RequestConfigValidationError(str(exc)) from exc

    if m in NO_REQUEST_BODY_METHODS and parsed.body is not None:
        raise RequestConfigValidationError(
            "request_config.body is not allowed for GET or DELETE actions"
        )

    dumped = dict(parsed.model_dump(mode="python", exclude_none=True))
    return dumped if dumped else None
