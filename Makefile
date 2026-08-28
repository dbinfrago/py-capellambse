# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
# vim:set fdm=marker:

# Most targets in this Makefile emit useful output to the user, which becomes
# messed up when parallelizing execution. On the other hand, there aren't any
# targets here which could actually benefit from parallelization - building the
# package is done by a single tool call, which would hold a lock file anyway.
.NOTPARALLEL:

.PHONY: help
help: #: Show this help
	@awk 'BEGIN { printf "\x1B[95mAvailable make targets:\x1B[m\n" } \
		{ if (match($$0, /^# (.*) \{\{\{1$$/, m)) { printf "\n\x1b[95m%s:\x1b[m\n", m[1] } \
		else if (match($$0, /^([^:]+): .*?#: (.*)/, m)) { printf "    \x1b[96m%-15s\x1b[m - %s\n", m[1], m[2] } }' Makefile

# Development {{{1

.PHONY: dev
dev: .venv  #: Set up development environment
.venv: pyproject.toml
	find src -type f \( -name '*.so' -o -name '*.pyd' \) -delete || true
	uv sync --inexact
	uv run --no-sync python -m maturin_import_hook site install
	touch -c .venv
	if [[ -d .jj ]]; then touch .jj/.maturin_hook_ignore; fi

.PHONY: install-hooks
install-hooks: dev .venv #: Install pre-commit hooks
	uv run --no-sync pre-commit install || :
	uv run --no-sync pre-commit install-hooks

.PHONY: rebuild
rebuild: clean dev #: Rebuild native Rust module
	uv sync --inexact --reinstall-package capellambse

.PHONY: clean
clean: #: Clean built library files
	find src -type f \( -name '*.so' -o -name '*.pyd' \) -delete || true

.PHONY: dist-clean
dist-clean: clean docs-clean #: Clean all build artifacts, tools and data
	find . -type d \( -name __pycache__ -o -name target \) -execdir rm -rf {} \; 2>/dev/null || true
	rm -rf .*cache .coverage .venv build dist htmlcov src/*.egg-info

# Testing {{{1

.PHONY: test
test: .venv #: Run unit tests
	uv run --no-sync pytest -n auto

.PHONY: coverage
coverage: .venv #: Run unit tests with coverage reporting
	uv run --no-sync pytest --cov=capellambse --cov-report=term
.coverage: $(shell find src tests -name "*.py")
	uv run --no-sync pytest --cov=capellambse --cov-report=term
htmlcov: .coverage #: Export coverage data as HTML
	uv run --no-sync coverage html -d $@
	touch -c $@
coverage.json: .coverage #: Export coverage data as JSON
	uv run --no-sync coverage json -o $@
coverage.lcov: .coverage #: Export coverage data as LCOV
	uv run --no-sync coverage lcov -o $@

.PHONY: lint
lint: .venv #: Run pre-commit checks on all files
	uv run --no-sync pre-commit run --all-files

.PHONY: verify-examples
verify-examples: #: Verify example notebooks
	uv run --no-sync ./scripts/verify-examples.sh

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

.PHONY: release
release: lint sdist wheel #: Tag a new release
	./scripts/release.py $${RELEASE_VERSION:+:--version=$$RELEASE_VERSION}

.PHONY: sdist
sdist: #: Build source distribution
	uv build --sdist

.PHONY: wheel
wheel: #: Build binary wheel distribution
	uv build --wheel
