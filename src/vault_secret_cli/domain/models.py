"""Domain objects used across the application."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Secret:
    """A Vault secret with metadata kept separate from secret values."""

    path: str
    data: dict[str, Any]
    version: int | None = None

    def require_key(self, key: str) -> Any:
        if key not in self.data:
            raise KeyError(key)
        return self.data[key]
