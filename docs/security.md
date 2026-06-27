# Security

## Threat model

This tool assumes Vault is the source of truth for secrets and the local machine is trusted enough to receive the requested values. It focuses on reducing accidental exposure through logs, diagnostics, and formatting.

## Practices

- Tokens are read from environment variables or `.env`; `.env` is ignored by Git.
- Diagnostics show token presence, not token contents.
- `inspect` prints key names and metadata only.
- Domain errors do not include secret values.
- CI runs secret scanning-friendly tests with fake data only.

## Recommended Vault policy

For a service that reads `secret/data/demo/*`:

```hcl
path "secret/data/demo/*" {
  capabilities = ["read"]
}

path "secret/metadata/demo/*" {
  capabilities = ["list", "read"]
}
```
