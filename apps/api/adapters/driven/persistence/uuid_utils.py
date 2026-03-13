"""UUID helpers shared by persistence adapters.

All helpers work with string UUIDs and are tolerant to both
32-char hex and canonical (dashed) forms.
"""
from __future__ import annotations

import uuid


def parse_uuid(value: str | None) -> uuid.UUID | None:
    """Parse UUID from string; accept hex or canonical. Returns None on error."""
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    try:
        if len(value) == 32 and "-" not in value:
            return uuid.UUID(hex=value)
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return None


def normalize_uuid(value: str | None) -> str | None:
    """Normalize UUID string to canonical form; returns original value on error."""
    if value is None:
        return None
    u = parse_uuid(value)
    return str(u) if u else value


def to_hex(value: str) -> str:
    """Convert canonical or hex UUID string to hex for DB storage."""
    u = parse_uuid(value)
    return u.hex if u else value


def canonical_to_hex(value: str) -> str | None:
    """Convert canonical UUID string to hex; returns None on error."""
    u = parse_uuid(value)
    return u.hex if u else None


def eq_uuid(a: str | None, b: str | None) -> bool:
    """Compare two UUID-ish strings regardless of hex vs canonical form."""
    ua = parse_uuid(a) if a is not None else None
    ub = parse_uuid(b) if b is not None else None
    if ua and ub:
        return ua == ub
    return a == b

