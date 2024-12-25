# Variables
PYTHON = python3.11
VENV_DIR = .venv
ACTIVATE = $(VENV_DIR)/bin/activate
REQ_FILE = setup/requirements.txt
INTEGRATION_TEST_SUBDIR = test/e2e

# Default target
.DEFAULT_GOAL := help

# Targets
help: ## Show this help message
	@echo "Available commands:"
	@awk -F ':|##' '/^[a-zA-Z0-9\._-]+:.*##/ { printf "  %-20s %s\n", $$1, $$3 }' $(MAKEFILE_LIST)

venv: ## Create a virtual environment
	$(PYTHON) -m venv $(VENV_DIR)

install: venv ## Install dependencies
	. $(ACTIVATE) && pip install -r $(REQ_FILE)

unittest: ## Run tests with pytest
	. $(ACTIVATE) && pytest

.PHONY: integration-test
integration-test: install
	$(PYTHON) -m pytest $(INTEGRATION_TEST_SUBDIR)

lint: ## Lint code with flake8
	. $(ACTIVATE) && flake8 .

clean: ## Remove temporary files and the virtual environment
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache .mypy_cache

.PHONY: help venv install test lint clean