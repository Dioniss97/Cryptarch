"""Unit tests for action input_schema JSON Schema subset (no DB)."""

import pytest

from core.domain.input_schema_contract import (
    InputSchemaValidationError,
    validate_and_normalize_input_schema_json,
)


def test_none_is_valid():
    assert validate_and_normalize_input_schema_json(None) is None


def test_minimal_object_schema():
    raw = {"type": "object", "properties": {}}
    assert validate_and_normalize_input_schema_json(raw) == raw


def test_rejects_non_object_root():
    with pytest.raises(InputSchemaValidationError, match="JSON object"):
        validate_and_normalize_input_schema_json("x")


def test_rejects_wrong_top_level_type():
    with pytest.raises(InputSchemaValidationError, match="'object'"):
        validate_and_normalize_input_schema_json({"type": "string"})


def test_rejects_legacy_fields_only_wrapper():
    with pytest.raises(InputSchemaValidationError, match="legacy"):
        validate_and_normalize_input_schema_json({"fields": [{"name": "a"}]})


def test_property_type_must_be_allowed():
    with pytest.raises(InputSchemaValidationError, match="properties\\['x'\\].type"):
        validate_and_normalize_input_schema_json(
            {
                "type": "object",
                "properties": {"x": {"type": "object"}},
            },
        )


def test_required_must_be_string_list():
    with pytest.raises(InputSchemaValidationError, match="required"):
        validate_and_normalize_input_schema_json(
            {"type": "object", "properties": {}, "required": [1]},
        )
