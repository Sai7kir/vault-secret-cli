"""Output formatters for secrets."""

from __future__ import annotations

import json
import re
import shlex
from collections.abc import Mapping
from typing import Any

from vault_secret_cli.domain.errors import ConfigurationError

_ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class JsonFormatter:
    def __init__(self, *, pretty: bool = False) -> None:
        self._pretty = pretty

    def format(self, values: Mapping[str, object]) -> str:
        indent = 2 if self._pretty else None
        return json.dumps(values, indent=indent, sort_keys=True)


class EnvFormatter:
    def format(self, values: Mapping[str, object]) -> str:
        lines: list[str] = []
        for key, value in values.items():
            env_key = _normalize_env_key(key)
            lines.append(f"{env_key}={_escape_dotenv_value(value)}")
        return "\n".join(lines)


class ShellFormatter:
    def format(self, values: Mapping[str, object]) -> str:
        lines: list[str] = []
        for key, value in values.items():
            env_key = _normalize_env_key(key)
            lines.append(f"export {env_key}={shlex.quote(_stringify(value))}")
        return "\n".join(lines)


class RawFormatter:
    def format(self, values: Mapping[str, object]) -> str:
        if len(values) != 1:
            raise ConfigurationError("raw output requires exactly one selected key")
        return _stringify(next(iter(values.values())))


def _normalize_env_key(key: str) -> str:
    env_key = key.upper().replace("-", "_").replace(".", "_")
    if not _ENV_KEY_PATTERN.match(env_key):
        raise ConfigurationError(
            f"secret key '{key}' cannot be represented as an environment variable"
        )
    return env_key


def _escape_dotenv_value(value: Any) -> str:
    text = _stringify(value)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)
