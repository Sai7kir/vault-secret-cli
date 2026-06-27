# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quality checks

```bash
make all
```

Pull requests should include tests for behavior changes and avoid printing real secrets in logs, snapshots, or docs.
