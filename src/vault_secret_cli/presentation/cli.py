"""Typer-based command line interface."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from vault_secret_cli import __version__
from vault_secret_cli.application.formatters import (
    EnvFormatter,
    JsonFormatter,
    RawFormatter,
    ShellFormatter,
)
from vault_secret_cli.application.services import SecretService
from vault_secret_cli.domain.errors import ConfigurationError, VaultSecretCliError
from vault_secret_cli.infrastructure.config import Settings
from vault_secret_cli.infrastructure.vault.client import HvacSecretReader

app = typer.Typer(
    name="vault-secret",
    help="Retrieve HashiCorp Vault KV v2 secrets without exposing them in logs.",
    no_args_is_help=True,
)
console = Console(stderr=True)


class OutputFormat(str, Enum):
    json = "json"
    pretty_json = "pretty-json"
    env = "env"
    shell = "shell"
    raw = "raw"


def main() -> None:
    app()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def callback(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=_version_callback, help="Show version and exit."),
    ] = None,
) -> None:
    """Configure the CLI."""


@app.command()
def get(
    path: Annotated[str, typer.Argument(help="KV v2 secret path, for example app/prod/db.")],
    key: Annotated[str | None, typer.Option("--key", "-k", help="Return only one key.")] = None,
    mount: Annotated[str | None, typer.Option("--mount", "-m", help="Vault KV mount name.")] = None,
    version: Annotated[int | None, typer.Option("--secret-version", help="KV v2 version.")] = None,
    output: Annotated[
        OutputFormat,
        typer.Option("--output", "-o", help="Output format."),
    ] = OutputFormat.json,
) -> None:
    """Read a secret and write the value to stdout."""
    settings = Settings()
    service = _build_service(settings)
    try:
        values = service.get_secret(
            path=path,
            mount=mount or settings.default_mount,
            key=key,
            version=version,
        )
        typer.echo(_formatter(output).format(values))
    except VaultSecretCliError as exc:
        _fail(exc)


@app.command("list")
def list_secrets(
    path: Annotated[str, typer.Argument(help="KV v2 folder path to list, for example app/prod.")],
    mount: Annotated[str | None, typer.Option("--mount", "-m", help="Vault KV mount name.")] = None,
) -> None:
    """List secret names under a path."""
    settings = Settings()
    service = _build_service(settings)
    try:
        keys = service.list_secrets(path=path, mount=mount or settings.default_mount)
    except VaultSecretCliError as exc:
        _fail(exc)

    for key in keys:
        typer.echo(key)


@app.command()
def inspect(
    path: Annotated[str, typer.Argument(help="KV v2 secret path to inspect.")],
    mount: Annotated[str | None, typer.Option("--mount", "-m", help="Vault KV mount name.")] = None,
    version: Annotated[int | None, typer.Option("--secret-version", help="KV v2 version.")] = None,
) -> None:
    """Show secret metadata and key names without printing secret values."""
    settings = Settings()
    service = _build_service(settings)
    try:
        secret = service.describe_secret(
            path=path,
            mount=mount or settings.default_mount,
            version=version,
        )
    except VaultSecretCliError as exc:
        _fail(exc)

    table = Table(title=f"{mount or settings.default_mount}/{path}")
    table.add_column("Property")
    table.add_column("Value")
    table.add_row("version", str(secret.version or "unknown"))
    table.add_row("keys", ", ".join(sorted(secret.data.keys())))
    console.print(table)


@app.command()
def doctor() -> None:
    """Validate local configuration without printing tokens."""
    try:
        settings = Settings()
    except Exception as exc:
        _fail(ConfigurationError(str(exc)))

    table = Table(title="Vault Secret CLI configuration")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("vault_addr", settings.safe_vault_addr)
    table.add_row("vault_token", "set" if settings.vault_token else "missing")
    table.add_row("vault_namespace", settings.vault_namespace or "not set")
    table.add_row("default_mount", settings.default_mount)
    table.add_row("verify_tls", str(settings.verify_tls))
    console.print(table)


def _build_service(settings: Settings) -> SecretService:
    return SecretService(HvacSecretReader(settings))


def _formatter(
    output: OutputFormat,
) -> JsonFormatter | EnvFormatter | ShellFormatter | RawFormatter:
    if output is OutputFormat.json:
        return JsonFormatter()
    if output is OutputFormat.pretty_json:
        return JsonFormatter(pretty=True)
    if output is OutputFormat.env:
        return EnvFormatter()
    if output is OutputFormat.shell:
        return ShellFormatter()
    return RawFormatter()


def _fail(exc: VaultSecretCliError) -> None:
    console.print(f"[red]error:[/red] {exc}")
    raise typer.Exit(code=1) from exc
