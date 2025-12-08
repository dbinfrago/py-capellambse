# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0

import collections.abc as cabc
import contextlib
import errno
import logging
import pathlib
import subprocess
import typing as t
from unittest import mock

import pytest

import capellambse
from capellambse.filehandler import git


def test_gitfilehandler_can_read_remote_files_no_revision() -> None:
    fh = capellambse.get_filehandler(
        "git+https://github.com/dbinfrago/py-capellambse.git"
    )
    assert isinstance(fh, git.GitFileHandler)
    assert fh.revision == "refs/heads/master"


def test_gitfilehandler_can_read_remote_files_with_revision() -> None:
    fh = capellambse.get_filehandler(
        "git+https://github.com/dbinfrago/py-capellambse.git",
        revision="gh-pages",
    )

    assert isinstance(fh, git.GitFileHandler)
    assert fh.revision == "refs/heads/gh-pages"


def test_GitFileHandler_locks_repo_during_tasks(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    did_ls_files = False

    def mock_run(
        cmd: cabc.Sequence[str],
        *args: t.Any,
        encoding: str = "",
        **kw: t.Any,
    ) -> mock.Mock:
        del args, kw
        nonlocal did_ls_files

        assert len(cmd) >= 1
        assert cmd[0] == "git"
        while len(cmd) >= 2 and cmd[1] == "-c":
            cmd = [cmd[0], *cmd[3:]]

        if len(cmd) >= 2 and cmd[1] == "ls-remote":
            assert not did_ls_files
            did_ls_files = True
            data = "0123456789abcdef0123456789abcdef01234567\thello"
            mock_return = mock.Mock()
            mock_return.stdout = data if encoding else data.encode("ascii")
            mock_return.stderr = "" if encoding else b""
            mock_return.returncode = 0
            return mock_return

        assert did_ls_files
        raise FileNotFoundError(errno.ENOENT, "--mocked end of test--")

    flocked_files: set[str] = set()

    @contextlib.contextmanager
    def mock_flock(file: pathlib.Path) -> cabc.Generator[None, None, None]:
        nonlocal flocked_files
        assert not flocked_files
        flocked_files.add(str(file))
        yield

    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(capellambse.helpers, "flock", mock_flock)
    caplog.set_level(logging.DEBUG)
    caplog.clear()

    with pytest.raises(FileNotFoundError, match=r"--mocked end of test--$"):
        capellambse.get_filehandler(
            "git+https://domain.invalid/demo.git", revision="somebranch"
        )

    assert did_ls_files
    assert len(flocked_files) == 1
