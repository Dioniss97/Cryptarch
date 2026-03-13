"""Input schema V1 validation and payload runtime checks."""
from __future__ import annotations

import re
from typing import Any


ALLOWED_TYPES = {"text", "textarea", "number", "boolean", "select", "radio", "date"}
I18N_PATHS = {
    "label",
    "placeholder",
    "helpText",
}


class InputSchemaValidationError(ValueError):
    pass


class PayloadValidationError(ValueError):
    def __init__(self, details: list[dict[str, str]]) -> None:
        super().__init__("Invalid payload")
        self.details = details


def validate_input_schema_v1(schema: dict[str, Any] | None) -> None:
    if schema is None:
        return
    if not isinstance(schema, dict):
        raise InputSchemaValidationError("Schema must be an object")
    fields = schema.get("fields")
    if not isinstance(fields, list):
        raise InputSchemaValidationError("Schema.fields must be a list")
    for idx, field in enumerate(fields):
        _validate_field(field, idx)


def validate_payload_against_schema(
    schema: dict[str, Any] | None, payload: dict[str, Any] | None
) -> None:
    if schema is None:
        return
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise PayloadValidationError(
            [{"field": "_root", "code": "type", "message": "Payload must be an object"}]
        )

    details: list[dict[str, str]] = []
    for field in schema.get("fields", []):
        name = field.get("name")
        field_type = field.get("type")
        required = bool(field.get("required"))
        value = payload.get(name)

        if required and name not in payload:
            details.append(
                {"field": name, "code": "required", "message": "Field is required"}
            )
            continue
        if name not in payload:
            continue
        if value is None and required:
            details.append(
                {"field": name, "code": "required", "message": "Field is required"}
            )
            continue
        if value is None:
            continue

        if not _value_matches_type(field_type, value):
            details.append(
                {
                    "field": name,
                    "code": "type",
                    "message": f"Expected type {field_type}",
                }
            )
            continue

        if field_type in {"select", "radio"}:
            options = field.get("options") or []
            allowed_values = {opt.get("value") for opt in options if isinstance(opt, dict)}
            if value not in allowed_values:
                details.append(
                    {
                        "field": name,
                        "code": "option",
                        "message": "Value is not part of allowed options",
                    }
                )
                continue

        validation = field.get("validation")
        if (
            isinstance(validation, dict)
            and isinstance(validation.get("regex"), str)
            and isinstance(value, str)
        ):
            regex = validation["regex"]
            if re.fullmatch(regex, value) is None:
                message = validation.get("message") or "Value does not match regex"
                details.append(
                    {"field": name, "code": "regex", "message": _i18n_to_text(message)}
                )

    if details:
        raise PayloadValidationError(details)


def _validate_field(field: Any, idx: int) -> None:
    if not isinstance(field, dict):
        raise InputSchemaValidationError(f"Field #{idx} must be an object")
    for key in ("type", "name", "label", "required"):
        if key not in field:
            raise InputSchemaValidationError(f"Field #{idx} missing required key '{key}'")

    field_type = field.get("type")
    if field_type not in ALLOWED_TYPES:
        raise InputSchemaValidationError(
            f"Field #{idx} has unsupported type '{field_type}'"
        )
    if not isinstance(field.get("name"), str) or not field["name"].strip():
        raise InputSchemaValidationError(f"Field #{idx} name must be a non-empty string")
    if not isinstance(field.get("required"), bool):
        raise InputSchemaValidationError(f"Field #{idx} required must be boolean")

    _validate_i18n_value(field.get("label"), f"Field #{idx}.label")
    for key in I18N_PATHS - {"label"}:
        if key in field:
            _validate_i18n_value(field.get(key), f"Field #{idx}.{key}")

    validation = field.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            raise InputSchemaValidationError(f"Field #{idx}.validation must be an object")
        regex = validation.get("regex")
        if regex is not None:
            if not isinstance(regex, str):
                raise InputSchemaValidationError(
                    f"Field #{idx}.validation.regex must be a string"
                )
            try:
                re.compile(regex)
            except re.error as exc:
                raise InputSchemaValidationError(
                    f"Field #{idx}.validation.regex is invalid: {exc}"
                ) from exc
        if "message" in validation:
            _validate_i18n_value(validation.get("message"), f"Field #{idx}.validation.message")

    if field_type in {"select", "radio"}:
        options = field.get("options")
        if not isinstance(options, list) or not options:
            raise InputSchemaValidationError(
                f"Field #{idx} options must be a non-empty list for {field_type}"
            )
        for opt_idx, option in enumerate(options):
            if not isinstance(option, dict):
                raise InputSchemaValidationError(
                    f"Field #{idx}.options[{opt_idx}] must be an object"
                )
            if "value" not in option or "label" not in option:
                raise InputSchemaValidationError(
                    f"Field #{idx}.options[{opt_idx}] requires value and label"
                )
            _validate_i18n_value(
                option.get("label"), f"Field #{idx}.options[{opt_idx}].label"
            )


def _validate_i18n_value(value: Any, path: str) -> None:
    if isinstance(value, str):
        return
    if isinstance(value, dict) and value:
        for key, item in value.items():
            if not isinstance(key, str) or not isinstance(item, str):
                raise InputSchemaValidationError(
                    f"{path} i18n map must be string->string"
                )
        return
    raise InputSchemaValidationError(f"{path} must be string or i18n map")


def _i18n_to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("es", "en"):
            if isinstance(value.get(key), str):
                return value[key]
        for item in value.values():
            if isinstance(item, str):
                return item
    return "Validation error"


def _value_matches_type(field_type: str, value: Any) -> bool:
    if field_type in {"text", "textarea", "select", "radio", "date"}:
        return isinstance(value, str)
    if field_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if field_type == "boolean":
        return isinstance(value, bool)
    return False
