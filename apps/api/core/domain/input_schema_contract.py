"""Canonical contract for Action.input_schema_json (JSON Schema subset).

Storage and API surface use a JSON Schema object: ``type: object`` with optional
``properties`` and ``required``. Admin builds this shape via ``buildSchemaFromFields``;
chat maps it to renderable fields at the UI boundary (see web ``chatFieldsFromInputSchemaJson``).
"""

from __future__ import annotations

from typing import Any

ALLOWED_PROPERTY_TYPES = frozenset({"string", "number", "integer", "boolean"})


class InputSchemaValidationError(ValueError):
    """input_schema_json is not a valid Cryptarch action input schema document."""


class ActionPayloadValidationError(ValueError):
    """User payload does not satisfy the action input_schema_json contract."""


def _property_type_ok(raw: Any) -> bool:
    if raw is None:
        return True
    if isinstance(raw, str):
        return raw in ALLOWED_PROPERTY_TYPES or raw == "null"
    if isinstance(raw, list):
        return all(
            isinstance(x, str) and (x in ALLOWED_PROPERTY_TYPES or x == "null")
            for x in raw
        )
    return False


def validate_and_normalize_input_schema_json(raw: Any) -> dict[str, Any] | None:
    """Validate ``input_schema_json`` for create/update. Returns the same dict or None.

    Rejects legacy chat-only shapes such as ``{"fields": [...]}`` without JSON Schema properties.
    """
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise InputSchemaValidationError("input_schema_json must be a JSON object")
    if "fields" in raw and "properties" not in raw:
        raise InputSchemaValidationError(
            "input_schema_json must follow JSON Schema (object with properties); "
            "legacy {fields: [...]} is not accepted on the API"
        )
    schema_type = raw.get("type")
    if schema_type is not None and schema_type != "object":
        raise InputSchemaValidationError(
            "input_schema_json.type must be 'object' when set"
        )
    properties = raw.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            raise InputSchemaValidationError(
                "input_schema_json.properties must be an object"
            )
        for key, definition in properties.items():
            if not isinstance(definition, dict):
                raise InputSchemaValidationError(
                    f"input_schema_json.properties[{key!r}] must be an object",
                )
            if not _property_type_ok(definition.get("type")):
                raise InputSchemaValidationError(
                    f"input_schema_json.properties[{key!r}].type must be a string, "
                    f"array of strings, or omitted (allowed: "
                    f"{', '.join(sorted(ALLOWED_PROPERTY_TYPES))}, null)",
                )
    required = raw.get("required")
    if required is not None:
        if not isinstance(required, list) or not all(
            isinstance(x, str) for x in required
        ):
            raise InputSchemaValidationError(
                "input_schema_json.required must be an array of strings",
            )
    return raw


def _value_matches_property_type(value: Any, expected_type: Any) -> bool:
    if expected_type is None:
        return True
    types: list[str]
    if isinstance(expected_type, str):
        types = [expected_type]
    elif isinstance(expected_type, list):
        types = [x for x in expected_type if isinstance(x, str)]
    else:
        return False
    for t in types:
        if t == "string" and isinstance(value, str):
            return True
        if t == "boolean" and isinstance(value, bool):
            return True
        if t == "integer" and type(value) is int and not isinstance(value, bool):
            return True
        if (
            t == "number"
            and type(value) in (int, float)
            and not isinstance(value, bool)
        ):
            return True
        if t == "null" and value is None:
            return True
    return False


def validate_action_payload(
    payload: Any, input_schema_json: dict[str, Any] | None
) -> dict[str, Any]:
    """Validate execute payload against action input_schema_json. Returns payload dict."""
    if not isinstance(payload, dict):
        raise ActionPayloadValidationError("payload must be a JSON object")
    if input_schema_json is None:
        return payload
    if not isinstance(input_schema_json, dict):
        return payload
    properties = input_schema_json.get("properties")
    if properties is not None and not isinstance(properties, dict):
        properties = {}
    elif properties is None:
        properties = {}
    required = input_schema_json.get("required")
    if required is not None:
        if not isinstance(required, list):
            required = []
        for key in required:
            if not isinstance(key, str):
                continue
            if key not in payload:
                raise ActionPayloadValidationError(
                    f"payload missing required property {key!r}"
                )
    for key, value in payload.items():
        definition = properties.get(key)
        if not isinstance(definition, dict):
            continue
        expected_type = definition.get("type")
        if expected_type is not None and not _value_matches_property_type(
            value, expected_type
        ):
            raise ActionPayloadValidationError(
                f"payload property {key!r} has invalid type for schema",
            )
    return payload
