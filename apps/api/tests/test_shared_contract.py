"""Sin Postgres: valida carga de packages/shared/data/domain.json y constantes."""

from shared_contract import (
    DOCUMENT_STATUS_QUEUED,
    ROLE_ADMIN,
    SAVED_FILTER_TARGET_USER,
    SESSION_STORAGE_KEY,
    TOKEN_TYPE_BEARER,
    UserRole,
)


def test_domain_json_loaded():
    assert ROLE_ADMIN == "admin"
    assert DOCUMENT_STATUS_QUEUED == "queued"
    assert SAVED_FILTER_TARGET_USER == "user"
    assert TOKEN_TYPE_BEARER == "bearer"
    assert SESSION_STORAGE_KEY == "cryptarch_session"
    assert UserRole.admin.value == "admin"
