from collections.abc import Sequence

import pytest
from typer.testing import CliRunner

from vault_secret_cli.application.services import SecretService
from vault_secret_cli.domain.models import Secret
from vault_secret_cli.presentation import cli

runner = CliRunner()


class FakeReader:
    def read_secret(self, path: str, mount: str, version: int | None = None) -> Secret:
        return Secret(
            path=path, data={"password": "secret", "username": "app"}, version=version or 1
        )

    def list_secrets(self, path: str, mount: str) -> Sequence[str]:
        return ["prod", "stage"]


def fake_build_service(settings: object) -> SecretService:
    return SecretService(FakeReader())


def test_get_outputs_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_build_service", fake_build_service)
    monkeypatch.setenv("VAULT_TOKEN", "test-token")

    result = runner.invoke(cli.app, ["get", "app/prod", "--key", "username"])

    assert result.exit_code == 0
    assert '"username": "app"' in result.stdout
    assert "test-token" not in result.stdout


def test_get_outputs_raw(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_build_service", fake_build_service)
    monkeypatch.setenv("VAULT_TOKEN", "test-token")

    result = runner.invoke(cli.app, ["get", "app/prod", "--key", "password", "--output", "raw"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "secret"


def test_list_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_build_service", fake_build_service)
    monkeypatch.setenv("VAULT_TOKEN", "test-token")

    result = runner.invoke(cli.app, ["list", "app"])

    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["prod", "stage"]
