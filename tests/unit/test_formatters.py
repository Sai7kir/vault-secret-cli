import json

import pytest

from vault_secret_cli.application.formatters import (
    EnvFormatter,
    JsonFormatter,
    RawFormatter,
    ShellFormatter,
)
from vault_secret_cli.domain.errors import ConfigurationError


def test_json_formatter_sorts_keys() -> None:
    rendered = JsonFormatter().format({"z": 1, "a": "b"})

    assert json.loads(rendered) == {"a": "b", "z": 1}
    assert rendered.index('"a"') < rendered.index('"z"')


def test_env_formatter_escapes_values_and_normalizes_keys() -> None:
    rendered = EnvFormatter().format({"db-password": 'pa"ss', "port": 5432})

    assert 'DB_PASSWORD="pa\\"ss"' in rendered
    assert 'PORT="5432"' in rendered


def test_shell_formatter_quotes_values() -> None:
    rendered = ShellFormatter().format({"password": "pa ss"})

    assert rendered == "export PASSWORD='pa ss'"


def test_raw_formatter_requires_one_value() -> None:
    with pytest.raises(ConfigurationError):
        RawFormatter().format({"a": "1", "b": "2"})


def test_raw_formatter_returns_string_value() -> None:
    assert RawFormatter().format({"password": "secret"}) == "secret"
