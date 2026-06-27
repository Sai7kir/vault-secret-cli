from collections.abc import Sequence

import pytest

from vault_secret_cli.application.services import SecretService
from vault_secret_cli.domain.errors import SecretNotFoundError
from vault_secret_cli.domain.models import Secret


class FakeReader:
    def __init__(self) -> None:
        self.secret = Secret(path="app/prod", data={"password": "secret", "port": 5432}, version=3)

    def read_secret(self, path: str, mount: str, version: int | None = None) -> Secret:
        assert path == "app/prod"
        assert mount == "secret"
        assert version in (None, 3)
        return self.secret

    def list_secrets(self, path: str, mount: str) -> Sequence[str]:
        assert path == "app"
        assert mount == "secret"
        return ["prod", "stage"]


def test_get_secret_returns_all_keys() -> None:
    service = SecretService(FakeReader())

    assert service.get_secret(path="app/prod", mount="secret") == {
        "password": "secret",
        "port": 5432,
    }


def test_get_secret_returns_selected_key() -> None:
    service = SecretService(FakeReader())

    assert service.get_secret(path="app/prod", mount="secret", key="password") == {
        "password": "secret"
    }


def test_get_secret_raises_for_missing_key() -> None:
    service = SecretService(FakeReader())

    with pytest.raises(SecretNotFoundError):
        service.get_secret(path="app/prod", mount="secret", key="missing")


def test_list_secrets() -> None:
    service = SecretService(FakeReader())

    assert service.list_secrets(path="app", mount="secret") == ["prod", "stage"]
