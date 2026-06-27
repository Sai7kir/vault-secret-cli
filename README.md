# Vault Secret CLI

A production-quality Python CLI for retrieving secrets from HashiCorp Vault KV v2 with a clean architecture, typed code, tests, Docker-based local Vault, and GitHub Actions.

## Why this project stands out

- Clean architecture: domain ports, application use cases, infrastructure adapters, and CLI presentation are separated.
- Secure defaults: tokens are read from the environment, never printed by diagnostics, and secret inspection shows key names only.
- Practical CLI output: JSON, pretty JSON, dotenv, shell export, and raw single-key modes.
- Recruiter-friendly engineering signals: tests, coverage, linting, typing, Docker, CI, publishing workflow, docs, and contribution files.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
vault-secret --help
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
vault-secret --help
```

## Local Vault demo

Start Vault:

```bash
docker compose up -d vault
```

Seed a demo secret:

```bash
docker compose run --rm vault-seed
```

Configure the CLI:

```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=dev-root-token
```

Read secrets:

```bash
vault-secret get demo/database --key username
vault-secret get demo/database --key password --output raw
vault-secret get demo/database --output env
vault-secret inspect demo/database
vault-secret list demo
```

## Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `VAULT_ADDR` | Vault server URL | `http://127.0.0.1:8200` |
| `VAULT_TOKEN` | Vault token used by hvac | unset |
| `VAULT_NAMESPACE` | Optional Vault Enterprise namespace | unset |
| `VAULT_SECRET_DEFAULT_MOUNT` | Default KV v2 mount | `secret` |
| `VAULT_SECRET_REQUEST_TIMEOUT_SECONDS` | HTTP request timeout | `10.0` |
| `VAULT_SECRET_VERIFY_TLS` | Verify TLS certificates | `true` |

## Commands

```bash
vault-secret get PATH [--key KEY] [--mount secret] [--secret-version N] [--output json]
vault-secret list PATH [--mount secret]
vault-secret inspect PATH [--mount secret]
vault-secret doctor
```

## Development

```bash
make install
make lint
make typecheck
make test
make all
```

## Architecture

```text
src/vault_secret_cli/
  domain/          Pure models, exceptions, and ports
  application/     Secret retrieval use cases and output formatters
  infrastructure/  HashiCorp Vault adapter and settings
  presentation/    Typer CLI
```

The application depends on `SecretReader`, not on `hvac`. This makes the behavior easy to test and keeps Vault SDK failures isolated in one adapter.

## Publishing

This repository includes a PyPI publishing workflow using trusted publishing. Configure a PyPI project for `vault-secret-cli`, then create a GitHub environment named `pypi`.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Security notes

- Do not commit real `.env` files or Vault tokens.
- Prefer short-lived Vault tokens and least-privilege policies.
- Use `inspect` when you need to debug key names without printing secret values.
- Use `--output raw` only for single-key reads and avoid shell history when pasting secrets into commands.
