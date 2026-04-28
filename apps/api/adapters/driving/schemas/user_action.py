"""Response shaping for user-facing action list (no request_config / connector secrets)."""

from typing import Any

from core.application.user_action_list import PermittedActionSummary

from adapters.driving.schemas.action import _canonical_str


def permitted_action_summary_to_response(row: PermittedActionSummary) -> dict[str, Any]:
    return {
        "id": _canonical_str(row.id),
        "name": row.name,
        "connector_id": _canonical_str(row.connector_id),
        "input_schema_json": row.input_schema_json,
        "input_schema_version": row.input_schema_version,
        "tag_ids": [_canonical_str(t) for t in row.tag_ids],
    }
