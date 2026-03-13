import pytest

from core.domain.input_schema import (
    InputSchemaValidationError,
    PayloadValidationError,
    validate_input_schema_v1,
    validate_payload_against_schema,
)


def _valid_schema():
    return {
        "fields": [
            {
                "type": "text",
                "name": "query",
                "label": {"es": "Consulta", "en": "Query"},
                "required": True,
                "validation": {
                    "regex": r"^[a-zA-Z0-9 ]+$",
                    "message": {"es": "Solo alfanumerico", "en": "Only alphanumeric"},
                },
            },
            {
                "type": "select",
                "name": "mode",
                "label": "Modo",
                "required": True,
                "options": [
                    {"value": "fast", "label": {"es": "Rapido", "en": "Fast"}},
                    {"value": "safe", "label": "Seguro"},
                ],
            },
            {
                "type": "boolean",
                "name": "dry_run",
                "label": "Simulacion",
                "required": False,
            },
        ]
    }


def test_validate_input_schema_v1_accepts_valid_schema():
    validate_input_schema_v1(_valid_schema())


def test_validate_input_schema_v1_rejects_invalid_regex():
    schema = _valid_schema()
    schema["fields"][0]["validation"]["regex"] = "("
    with pytest.raises(InputSchemaValidationError):
        validate_input_schema_v1(schema)


def test_validate_input_schema_v1_rejects_missing_required_key():
    schema = _valid_schema()
    schema["fields"][1].pop("required")
    with pytest.raises(InputSchemaValidationError):
        validate_input_schema_v1(schema)


def test_validate_payload_against_schema_rejects_type_and_option_errors():
    with pytest.raises(PayloadValidationError) as exc:
        validate_payload_against_schema(
            _valid_schema(),
            {"query": 1, "mode": "invalid"},
        )
    codes = {detail["code"] for detail in exc.value.details}
    assert "type" in codes
    assert "option" in codes


def test_validate_payload_against_schema_rejects_regex_error():
    with pytest.raises(PayloadValidationError) as exc:
        validate_payload_against_schema(
            _valid_schema(),
            {"query": "###", "mode": "safe"},
        )
    assert exc.value.details[0]["code"] == "regex"
