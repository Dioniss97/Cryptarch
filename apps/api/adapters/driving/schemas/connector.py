"""Request/response schemas and serialization for Connectors."""
import uuid
from pydantic import BaseModel


def _parse_uuid(value: str) -> uuid.UUID | None:
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if len(value) == 32 and "-" not in value:
            return uuid.UUID(hex=value)
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None


class ConnectorCreateBody(BaseModel):
    base_url: str
    auth_config: dict | None = None


class ConnectorUpdateBody(BaseModel):
    base_url: str | None = None
    auth_config: dict | None = None


def connector_to_response(connector) -> dict:
    """Serialize Connector to response dict. id and tenant_id in canonical form."""
    ci = _parse_uuid(str(connector.id)) if getattr(connector, "id", None) else None
    ti = (
        _parse_uuid(str(connector.tenant_id))
        if getattr(connector, "tenant_id", None)
        else None
    )
    return {
        "id": str(ci) if ci else str(getattr(connector, "id", "")),
        "tenant_id": str(ti) if ti else str(getattr(connector, "tenant_id", "")),
        "base_url": connector.base_url,
        "auth_config": getattr(connector, "auth_config", None),
    }
