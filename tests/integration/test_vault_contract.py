"""Optional integration smoke test.

Run this after starting the dev Vault from docker-compose:

    pytest tests/integration --run-vault-integration
"""

import os

import pytest

from vault_secret_cli.application.services import SecretService
from vault_secret_cli.infrastructure.config import Settings
from vault_secret_cli.infrastructure.vault.client import HvacSecretReader


@pytest.mark.vault_integration
def test_can_read_seeded_dev_secret() -> None:
    settings = Settings(
        vault_addr=os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200"),
        vault_token=os.environ.get("VAULT_TOKEN", "dev-root-token"),
        default_mount="secret",
        verify_tls=False,
    )
    service = SecretService(HvacSecretReader(settings))

    result = service.get_secret(path="demo/database", mount="secret", key="username")

    assert result == {"username": "demo"}
