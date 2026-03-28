"""Unit tests for action request_config validation (method vs body)."""

import pytest
from core.domain.action_request_config import (
    RequestConfigValidationError,
    validate_and_normalize_request_config,
)


def test_get_without_body_ok():
    assert validate_and_normalize_request_config("GET", None) is None
    assert validate_and_normalize_request_config("GET", {"timeout": 30}) == {
        "timeout": 30
    }
    assert validate_and_normalize_request_config(
        "GET", {"headers": {"X-Foo": "bar"}}
    ) == {"headers": {"X-Foo": "bar"}}


def test_get_with_body_rejected():
    with pytest.raises(RequestConfigValidationError, match="body"):
        validate_and_normalize_request_config("GET", {"body": {"k": 1}})


def test_delete_with_body_rejected():
    with pytest.raises(RequestConfigValidationError):
        validate_and_normalize_request_config("DELETE", {"body": []})


def test_post_put_patch_allow_body():
    cfg = {"body": {"a": 1}, "query": {"q": "x"}}
    assert validate_and_normalize_request_config("POST", cfg) == cfg
    assert validate_and_normalize_request_config("put", cfg) == cfg
    assert validate_and_normalize_request_config("PATCH", cfg) == cfg


def test_invalid_payload_not_object():
    with pytest.raises(RequestConfigValidationError, match="object"):
        validate_and_normalize_request_config("POST", "nope")  # type: ignore[arg-type]
