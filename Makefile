# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
# vim:set fdm=marker:

.PHONY: help
help: #: Show this help
	@awk 'BEGIN { printf "\x1B[95mAvailable make targets:\x1B[m\n" } \
		{ if (match($$0, /^# (.*) \{\{\{1$$/, m)) { printf "\n\x1b[95m%s:\x1b[m\n", m[1] } \
		else if (match($$0, /^([^:]+): .*?#: (.*)/, m)) { printf "    \x1b[96m%-15s\x1b[m - %s\n", m[1], m[2] } }' Makefile

# Development {{{1

.PHONY: dev
dev: .venv  #: Set up development environment
.venv: pyproject.toml
	uv sync --inexact
	touch -c .venv

.PHONY: install-hooks
install-hooks: dev .venv #: Install pre-commit hooks
	.venv/bin/pre-commit install || :
	.venv/bin/pre-commit install-hooks

.PHONY: rebuild
rebuild: #: Rebuild native Rust module
	uv sync --inexact --reinstall-package capellambse

.PHONY: clean
clean: docs-clean #: Clean all build artifacts
	find . -type d -name __pycache__ -execdir rm -rf {} \; 2>/dev/null || true
	rm -rf .*cache .coverage .venv build dist htmlcov src/*.egg-info

# Testing {{{1

.PHONY: test
test: .venv #: Run unit tests
	.venv/bin/pytest -n auto

.PHONY: coverage
coverage: .venv #: Run unit tests with coverage reporting
	.venv/bin/pytest --cov=capellambse --cov-report=term
.coverage: $(shell find src tests -name "*.py")
	.venv/bin/pytest --cov=capellambse --cov-report=term
htmlcov: .coverage #: Export coverage data as HTML
	.venv/bin/coverage html -d $@
	touch -c $@
coverage.json: .coverage #: Export coverage data as JSON
	.venv/bin/coverage json -o $@
coverage.lcov: .coverage #: Export coverage data as LCOV
	.venv/bin/coverage lcov -o $@

.PHONY: lint
lint: .venv #: Run pre-commit checks on all files
	.venv/bin/pre-commit run --all-files

.PHONY: verify-examples
verify-examples: #: Verify example notebooks
	./scripts/verify-examples.sh

# Documentation {{{1

.PHONY: docs
docs: #: Build documentation
	$(MAKE) -C docs html

.PHONY: docs-serve
docs-serve: #: Build and serve documentation locally
	$(MAKE) -C docs serve

.PHONY: docs-clean
docs-clean: #: Clean documentation build
	$(MAKE) -C docs clean

.PHONY: jupyter
jupyter: #: Start Jupyter Lab for examples
	cd docs/source/examples && CAPELLAMBSE_UUID_SEED=0 ../../../.venv/bin/jupyter lab

# Build & Distribution {{{1

.PHONY: sdist
sdist: #: Build source distribution
	uv build --sdist

.PHONY: wheel
wheel: #: Build binary wheel distribution
	uv build --wheel
