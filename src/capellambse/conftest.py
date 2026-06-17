# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Test fixtures for capellambse's doctests."""

from __future__ import annotations

import collections.abc as cabc
import typing as t

import pytest

import capellambse
from capellambse import helpers


@pytest.fixture(autouse=True)
def load_test_models(doctest_namespace: dict[str, t.Any]) -> None:
    model = capellambse.loadcli("test-7.0")
    doctest_namespace["model"] = model
    doctest_namespace["loader"] = model._loader


@pytest.fixture(autouse=True)
def deterministic_ids() -> cabc.Iterator[None]:
    with helpers.deterministic_ids():
        yield
