import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--run-vault-integration", action="store_true", default=False)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "vault_integration: requires a running Vault server")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-vault-integration"):
        return
    skip = pytest.mark.skip(reason="requires --run-vault-integration")
    for item in items:
        if "vault_integration" in item.keywords:
            item.add_marker(skip)
