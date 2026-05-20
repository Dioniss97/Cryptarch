"""Request/response schemas for POST /actions/{action_id}/execute."""

from typing import Any

from core.application.user_action_execute import ExecuteActionResult
from pydantic import BaseModel

from adapters.driving.schemas.action import _canonical_str


class ExecuteActionBody(BaseModel):
    payload: dict[str, Any] = {}


def execute_action_result_to_response(result: ExecuteActionResult) -> dict[str, Any]:
    return {
        "status": result.status,
        "message": result.message,
        "action_id": _canonical_str(result.action_id),
        "received_payload": result.received_payload,
    }
