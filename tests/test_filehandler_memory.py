# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from capellambse.filehandler import memory

TEST_CONTENT = b"Hello, World!"


@pytest.fixture
def fh() -> memory.MemoryFileHandler:
    fh = memory.MemoryFileHandler()
    with fh.open("test.txt", "w") as f:
        f.write(TEST_CONTENT)
    return fh


@pytest.fixture
def fhdir() -> memory.MemoryFileHandler:
    fh = memory.MemoryFileHandler()
    fh.write_file("top.txt", TEST_CONTENT)
    fh.write_file("some/test.txt", TEST_CONTENT)
    fh.write_file("some/test2.txt", TEST_CONTENT)
    fh.write_file("other/test3.txt", TEST_CONTENT)
    return fh


def test_MemoryFileHandler_raises_ValueError_for_invalid_path() -> None:
    with pytest.raises(ValueError, match="MemoryFileHandler"):
        memory.MemoryFileHandler(path="memory://invalid")


def test_MemoryFileHandler_raises_FileNotFoundError_for_nonexistent_file() -> (
    None
):
    fh = memory.MemoryFileHandler()
    with pytest.raises(FileNotFoundError):
        fh.open("test.txt")


def test_MemoryFileHandler_preserves_written_data(
    fh: memory.MemoryFileHandler,
) -> None:
    with fh.open("test.txt", "r") as f:
        assert f.read() == TEST_CONTENT


def test_MemoryFiles_return_bytes_objects_from_read(
    fh: memory.MemoryFileHandler,
) -> None:
    with fh.open("test.txt", "r") as f:
        assert isinstance(f.read(), bytes)


def test_empty_MemoryFileHandler_has_no_files() -> None:
    fh = memory.MemoryFileHandler()
    assert not [p.name for p in fh.iterdir()]


def test_MemoryFileHandler_iterates_over_files(
    fh: memory.MemoryFileHandler,
) -> None:
    assert [p.name for p in fh.iterdir()] == ["test.txt"]


def test_MemoryFileHandler_iterated_files_can_be_read(
    fh: memory.MemoryFileHandler,
) -> None:
    for p in fh.iterdir():
        with p.open("rb") as f:
            assert f.read() == TEST_CONTENT


def test_MemoryFilePath_returns_correct_name() -> None:
    fh = memory.MemoryFileHandler()
    assert fh.rootdir.joinpath("test.txt").name == "test.txt"


def test_MemoryFilePath_recognizes_files(fh: memory.MemoryFileHandler) -> None:
    assert fh.rootdir.joinpath("test.txt").is_file()


def test_MemoryFilePath_recognizes_directories(
    fh: memory.MemoryFileHandler,
) -> None:
    assert fh.rootdir.is_dir()


def test_MemoryFileHandler_can_iterate_subdirs(
    fhdir: memory.MemoryFileHandler,
) -> None:
    actual = [p.name for p in fhdir.rootdir.iterdir("some")]

    assert actual == ["test.txt", "test2.txt"]


def test_MemoryFilePath_can_be_iterated(
    fhdir: memory.MemoryFileHandler,
) -> None:
    actual = [p.name for p in fhdir.rootdir.joinpath("some").iterdir()]

    assert actual == ["test.txt", "test2.txt"]


def test_MemoryFilePath_can_iterate_over_subdirs(
    fhdir: memory.MemoryFileHandler,
) -> None:
    actual = [p.name for p in fhdir.rootdir.iterdir("some")]

    assert actual == ["test.txt", "test2.txt"]
