"""Dev seed: solo corre en APP_ENV development."""

from adapters.driven.persistence import dev_seed


def test_ensure_dev_admin_skips_when_not_development(monkeypatch):
    monkeypatch.setattr(dev_seed, "APP_ENV", "production")
    dev_seed.ensure_dev_admin()
