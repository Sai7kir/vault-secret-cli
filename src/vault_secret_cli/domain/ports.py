"""Ports that keep application use cases independent of Vault SDK details."""

from collections.abc import Mapping, Sequence
from typing import Protocol

from vault_secret_cli.domain.models import Secret


class SecretReader(Protocol):
    """Read-only secret repository contract."""

    def read_secret(self, path: str, mount: str, version: int | None = None) -> Secret:
        """Read a secret from Vault."""

    def list_secrets(self, path: str, mount: str) -> Sequence[str]:
        """List secret keys under a Vault path."""


class SecretFormatter(Protocol):
    """Format secrets for CLI output."""

    def format(self, values: Mapping[str, object]) -> str:
        """Return a string representation that is safe for stdout."""
