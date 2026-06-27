"""Configuration loaded from environment variables and CLI flags."""

from __future__ import annotations

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings.

    Environment variables use the VAULT_SECRET_ prefix, except VAULT_ADDR and VAULT_TOKEN,
    which are supported for compatibility with the official Vault CLI.
    """

    model_config = SettingsConfigDict(
        env_prefix="VAULT_SECRET_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    vault_addr: AnyHttpUrl = Field(
        default_factory=lambda: AnyHttpUrl("http://127.0.0.1:8200"),
        validation_alias="VAULT_ADDR",
    )
    vault_token: SecretStr | None = Field(default=None, validation_alias="VAULT_TOKEN")
    vault_namespace: str | None = Field(default=None, validation_alias="VAULT_NAMESPACE")
    default_mount: str = "secret"
    request_timeout_seconds: float = 10.0
    verify_tls: bool = True

    @property
    def safe_vault_addr(self) -> str:
        return str(self.vault_addr).rstrip("/")
