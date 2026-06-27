"""HashiCorp Vault adapter implemented with hvac."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import hvac
from hvac.exceptions import Forbidden, InvalidPath, VaultError

from vault_secret_cli.domain.errors import (
    AuthenticationError,
    SecretNotFoundError,
    VaultConnectionError,
    VaultPermissionError,
)
from vault_secret_cli.domain.models import Secret
from vault_secret_cli.infrastructure.config import Settings


class HvacSecretReader:
    """Read-only Vault KV v2 adapter."""

    def __init__(self, settings: Settings) -> None:
        token = settings.vault_token.get_secret_value() if settings.vault_token else None
        self._client = hvac.Client(
            url=settings.safe_vault_addr,
            token=token,
            namespace=settings.vault_namespace,
            timeout=settings.request_timeout_seconds,
            verify=settings.verify_tls,
        )

    def read_secret(self, path: str, mount: str, version: int | None = None) -> Secret:
        self._ensure_authenticated()
        try:
            response = self._client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=mount,
                version=version,
                raise_on_deleted_version=True,
            )
        except InvalidPath as exc:
            raise SecretNotFoundError(
                f"secret path '{path}' was not found in mount '{mount}'"
            ) from exc
        except Forbidden as exc:
            raise VaultPermissionError(f"permission denied reading '{mount}/{path}'") from exc
        except VaultError as exc:
            raise VaultConnectionError(
                f"Vault request failed while reading '{mount}/{path}'"
            ) from exc

        payload = response.get("data", {})
        data = payload.get("data")
        metadata = payload.get("metadata", {})
        if not isinstance(data, dict):
            raise SecretNotFoundError(f"secret path '{path}' did not contain key-value data")

        return Secret(path=path, data=data, version=_parse_version(metadata))

    def list_secrets(self, path: str, mount: str) -> Sequence[str]:
        self._ensure_authenticated()
        try:
            response = self._client.secrets.kv.v2.list_secrets(path=path, mount_point=mount)
        except InvalidPath as exc:
            raise SecretNotFoundError(
                f"secret path '{path}' was not found in mount '{mount}'"
            ) from exc
        except Forbidden as exc:
            raise VaultPermissionError(f"permission denied listing '{mount}/{path}'") from exc
        except VaultError as exc:
            raise VaultConnectionError(
                f"Vault request failed while listing '{mount}/{path}'"
            ) from exc

        keys = response.get("data", {}).get("keys", [])
        if not isinstance(keys, list):
            return []
        return [str(key) for key in keys]

    def _ensure_authenticated(self) -> None:
        try:
            if not self._client.is_authenticated():
                raise AuthenticationError(
                    "Vault authentication failed; set VAULT_TOKEN or login first"
                )
        except VaultError as exc:
            raise VaultConnectionError("could not verify Vault authentication") from exc


def _parse_version(metadata: dict[str, Any]) -> int | None:
    value = metadata.get("version")
    return value if isinstance(value, int) else None
