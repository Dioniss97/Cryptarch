"""Crea tenant y usuario admin de demo solo en entorno development."""

from __future__ import annotations

import logging

from sqlalchemy.exc import SQLAlchemyError

from adapters.driven.persistence.db import SessionLocal
from adapters.driven.persistence.models import TenantOrm, UserOrm
from adapters.driven.persistence.password_hasher import PasswordHasherImpl
from adapters.driven.persistence.uuid_utils import parse_uuid
from config import (
    APP_ENV,
    DEV_ADMIN_EMAIL,
    DEV_ADMIN_PASSWORD,
    DEV_SEED_TENANT_ID,
)
from shared_contract import ROLE_ADMIN

logger = logging.getLogger(__name__)


def ensure_dev_admin() -> None:
    """Idempotente: asegura tenant fijo y admin si APP_ENV es development/dev."""
    if APP_ENV.lower() not in ("development", "dev"):
        return

    tid = parse_uuid(DEV_SEED_TENANT_ID.strip())
    if not tid:
        logger.warning("DEV_SEED_TENANT_ID invalid; skip dev seed")
        return

    tenant_pk = tid.hex
    session = SessionLocal()
    try:
        tenant = session.query(TenantOrm).filter(TenantOrm.id == tenant_pk).first()
        if not tenant:
            session.add(TenantOrm(id=tenant_pk, name="Dev tenant"))
            session.flush()

        user = (
            session.query(UserOrm)
            .filter(
                UserOrm.tenant_id == tenant_pk,
                UserOrm.email == DEV_ADMIN_EMAIL,
            )
            .first()
        )
        if not user:
            hasher = PasswordHasherImpl()
            session.add(
                UserOrm(
                    tenant_id=tenant_pk,
                    email=DEV_ADMIN_EMAIL,
                    role=ROLE_ADMIN,
                    password_hash=hasher.hash(DEV_ADMIN_PASSWORD),
                )
            )
        session.commit()
        logger.info(
            "Dev seed OK: tenant_id=%s email=%s (password from DEV_ADMIN_PASSWORD)",
            DEV_SEED_TENANT_ID,
            DEV_ADMIN_EMAIL,
        )
    except SQLAlchemyError:
        session.rollback()
        logger.exception(
            "Dev seed failed (¿migraciones sin aplicar?). "
            "Ejecuta alembic upgrade head en la base de datos."
        )
    finally:
        session.close()
