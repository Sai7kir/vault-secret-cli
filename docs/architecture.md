# Architecture

Vault Secret CLI follows a small clean architecture layout.

## Layers

- `domain`: Pure Python types, errors, and ports. This layer has no dependency on Vault, Typer, or Rich.
- `application`: Use cases such as retrieving a secret key and formatting output.
- `infrastructure`: External systems. The `HvacSecretReader` adapter converts `hvac` responses and exceptions into domain objects and errors.
- `presentation`: The Typer CLI. It parses flags, calls use cases, and handles expected errors.

## Design choices

The CLI supports read-only KV v2 operations because secret retrieval is the high-value path and the safest surface for automation. Write support can be added later as a separate port and command group.

Errors intentionally avoid including secret values. The `doctor` and `inspect` commands expose configuration status and key names, but not tokens or values.
