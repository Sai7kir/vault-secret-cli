"""Application use cases for reading and presenting secrets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vault_secret_cli.domain.errors import SecretNotFoundError
from vault_secret_cli.domain.models import Secret
from vault_secret_cli.domain.ports import SecretReader


class SecretService:
    """Coordinates secret retrieval without depending on a concrete Vault SDK."""

    def __init__(self, reader: SecretReader) -> None:
        self._reader = reader

    def get_secret(
        self,
        *,
        path: str,
        mount: str,
        key: str | None = None,
        version: int | None = None,
    ) -> Mapping[str, object]:
        secret = self._reader.read_secret(path=path, mount=mount, version=version)
        if key is None:
            return secret.data
        try:
            return {key: secret.require_key(key)}
        except KeyError as exc:
            raise SecretNotFoundError(f"secret key '{key}' was not found at '{path}'") from exc

    def describe_secret(self, *, path: str, mount: str, version: int | None = None) -> Secret:
        return self._reader.read_secret(path=path, mount=mount, version=version)

    def list_secrets(self, *, path: str, mount: str) -> Sequence[str]:
        return self._reader.list_secrets(path=path, mount=mount)
