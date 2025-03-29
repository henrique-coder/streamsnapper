PYTHON ?= python3
VENV := .venv

.PHONY: setup-venv install lint format tests demo help
.DEFAULT_GOAL := help

install:
	poetry update
	poetry install

lint:
	poetry run ruff check

format:
	poetry run ruff format

tests:
	poetry run pytest -v --xfail-tb

help:
	@echo "Available commands:"
	@echo "  install     - Update dependencies, poetry.lock file, and install project"
	@echo "  lint        - Check code with ruff"
	@echo "  format      - Format code with ruff"
	@echo "  tests       - Run tests with pytest"
	@echo "  help        - Show this help message"
