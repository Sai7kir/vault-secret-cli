.PHONY: all install lint format typecheck test integration build clean

all: lint typecheck test

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff check --fix src tests
	ruff format src tests

typecheck:
	mypy src tests

test:
	pytest

integration:
	pytest tests/integration --run-vault-integration

build:
	python -m pip install build
	python -m build

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.mypy_cache','.ruff_cache','build','dist','htmlcov']]; [p.unlink() for p in pathlib.Path('.').glob('coverage.xml')]"
