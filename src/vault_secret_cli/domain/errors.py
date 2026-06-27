"""Domain-specific exceptions with safe, non-secret messages."""


class VaultSecretCliError(Exception):
    """Base exception for expected application errors."""


class AuthenticationError(VaultSecretCliError):
    """Raised when Vault authentication fails."""


class SecretNotFoundError(VaultSecretCliError):
    """Raised when a requested secret path or key is missing."""


class VaultConnectionError(VaultSecretCliError):
    """Raised when Vault cannot be reached."""


class VaultPermissionError(VaultSecretCliError):
    """Raised when Vault denies access to the requested resource."""


class ConfigurationError(VaultSecretCliError):
    """Raised when required configuration is missing or invalid."""
