"""
Re-export permission resolution from driven adapter (hexagonal).
Logic lives in adapters.driven.persistence.permission_query; this keeps legacy API.
"""
from adapters.driven.persistence.permission_query import (
    entity_has_all_filter_tags,
    resolve_effective_action_ids,
    resolve_effective_document_ids,
)

__all__ = [
    "entity_has_all_filter_tags",
    "resolve_effective_action_ids",
    "resolve_effective_document_ids",
]
