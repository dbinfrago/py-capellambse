#!/usr/bin/env python
# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import base64
import collections
import dataclasses
import enum
import io
import logging
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import typing as t

import awesomeversion
import click

from capellambse import helpers

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONCOM = re.compile(
    r"^(?P<type>\w+)(?:\((?P<scope>[A-Za-z0-9_-]+)\))?(?P<breaking>\!)?: (?P<subject>.*)$"
)
MAILUSER = re.compile(
    r"^(?:\d+\+)?(?P<user>[^@]+)@users\.noreply\.github\.com$"
)

logger = logging.getLogger(__name__)


class VersionBump(enum.IntEnum):
    MAJOR = 1
    MINOR = 2
    PATCH = 3


class CommitType(enum.Enum):
    BAD = "Commits with malformed subject lines"
    revert = "Reverted earlier changes"
    feat = "New features"
    perf = "Performance improvements"
    fix = "Bug fixes"
    docs = "Documentation changes"
    build = "Build system changes"
    ci = "CI/CD changes"
    test = "Unit test changes"
    refactor = "Code refactorings"
    merge = chore = None


@dataclasses.dataclass(frozen=True)
class CommitEntry:
    hash: str
    user: str
    type: CommitType
    scope: str | None
    breaking: bool
    subject: str


ParsedCommitLog: t.TypeAlias = dict[CommitType, list[CommitEntry]]


def _validate_version_tag(
    ctx: click.Context | None, param: click.Parameter | None, value: str | None
) -> awesomeversion.AwesomeVersion | None:
    del ctx, param
    if value is None:
        return None
    value = value.removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise click.UsageError(
            f"Invalid version format: {value!r}, expected format 'vX.Y.Z'"
        )
    return awesomeversion.AwesomeVersion(
        value,
        ensure_strategy=awesomeversion.AwesomeVersionStrategy.SEMVER,
    )


@click.command()
@click.option(
    "--prev",
    callback=_validate_version_tag,
    help=(
        "Tag of the previous version for changelog generation. "
        "Defaults to auto-detection based on git history."
    ),
)
@click.option(
    "--head",
    help=(
        "The commit to tag with the new version. "
        "Defaults to the current workspace commit or HEAD."
    ),
)
@click.option(
    "--version",
    callback=_validate_version_tag,
    help=(
        "New version, in the format 'vX.Y.Z'. "
        "If not given, uses conventional commits and semantic versioning "
        "based on the '--prev' tag and '--head' commit."
    ),
)
def _main(
    *,
    prev: awesomeversion.AwesomeVersion | None,
    head: str | None,
    version: awesomeversion.AwesomeVersion | None,
) -> None:
    logging.basicConfig()

    if not pathlib.Path(".git").exists():
        raise SystemExit("This script must be run in the repository root")

    if not head:
        head = _latest_commit()
    else:
        head = _exec("git", "log", "-1", "--format=%H", head)

    if not prev:
        prev_tag = _exec("git", "describe", "--tags", "--abbrev=0", head)
        prev = _validate_version_tag(None, None, prev_tag)
        assert prev is not None
    commit_log = _parse_commit_log(prev, head)

    if version:
        logger.info("MANUAL version bump from %s to %s", prev, version)
    else:
        if any(c.breaking for tc in commit_log.values() for c in tc):
            bump = VersionBump.MAJOR
        elif commit_log.get(CommitType.feat):
            bump = VersionBump.MINOR
        else:
            bump = VersionBump.PATCH
        version = _bump_version(prev, bump)
        logger.info("%s version bump from %s to %s", bump.name, prev, version)

    changelog = _format_changelog(commit_log)
    _create_git_tag(head, version, changelog)
    changelog = _read_tag_message(version) or changelog
    _copy_to_clipboard(changelog)


def _latest_commit() -> str:
    if (
        pathlib.Path(".jj").exists()
        and shutil.which("jj") is not None
        and not _exec(
            "jj",
            "log",
            "--no-graph",
            "-r@",
            "-Tif(empty && parents.len() < 2, 'empty')",
        )
    ):
        _exec("jj", "sign", "-r", "::@ & ~signed() & ~immutable()")
        return _exec("jj", "log", "--no-graph", "-r@", "-Tcommit_id")
    return _exec("git", "log", "-1", "--format=%H")


def _parse_commit_log(
    since: awesomeversion.AwesomeVersion,
    until: str,
    /,
) -> ParsedCommitLog:
    try:
        with open("authors.toml", "rb") as f:
            authormap: dict[str, str] = tomllib.load(f)
    except FileNotFoundError:
        logger.warning("authors.toml not found, cannot map authors to users")
        authormap = {}

    commits: ParsedCommitLog = collections.defaultdict(list)
    commitlog = _exec(
        "git", "log", "--format=%H%x00%aE%x00%s", "-z", f"v{since}..{until}"
    )
    assert commitlog.endswith("\x00")
    commitlog = commitlog[:-1]
    for commitid, author, msg in helpers.batched(
        commitlog.split("\x00"), 3, strict=True
    ):
        if author_match := MAILUSER.search(author):
            author = "@" + author_match.group("user")
        else:
            try:
                author = authormap[author]
            except KeyError:
                logger.warning(
                    "Unknown author for commit %s: %s", commitid, author
                )

        if msg.startswith("Merge pull request #"):
            msg = f"merge: {msg}"
        if not (msg_match := CONCOM.fullmatch(msg)):
            logger.warning("Bad commit subject: %s %s", commitid, msg)
            entry = CommitEntry(
                hash=commitid,
                user=author,
                type=CommitType.BAD,
                scope=None,
                breaking=False,
                subject=msg,
            )
            commits[CommitType.BAD].append(entry)
            continue

        ctype_name, scope, breaking, subject = msg_match.group(
            "type", "scope", "breaking", "subject"
        )
        try:
            ctype = CommitType[ctype_name]
        except KeyError:
            logger.warning(
                "Unknown commit type %r in %s", ctype_name, commitid
            )
            ctype = CommitType.BAD
            scope = None
            subject = msg

        entry = CommitEntry(
            hash=commitid,
            user=author,
            type=ctype,
            scope=scope,
            breaking=breaking == "!",
            subject=subject,
        )
        commits[ctype].append(entry)

    return commits


def _format_changelog(commit_log: ParsedCommitLog) -> str:
    writer = io.StringIO()
    breaking: list[CommitEntry] = []

    for ctype in CommitType:
        if ctype.value is None or ctype not in commit_log:
            continue

        writer.write(f"## {ctype.value}\n\n")
        for commit in reversed(commit_log.get(ctype, [])):
            writer.write("- ")
            if commit.scope:
                writer.write(f"**{commit.scope}**: ")
            writer.write(
                f"{commit.subject} *by {commit.user}* ({commit.hash})\n"
            )
        writer.write("\n")

    full_log = writer.getvalue()
    if not breaking:
        return full_log

    writer = io.StringIO()
    writer.write("# Breaking changes\n\n")
    for commit in breaking:
        writer.write("- ")
        if commit.scope:
            writer.write(f"**{commit.scope}**: ")
        writer.write(f"{commit.subject}\n")
    writer.write("\n# Full changelog\n\n")
    return writer.getvalue() + full_log


def _bump_version(
    version: awesomeversion.AwesomeVersion,
    bump: VersionBump,
    /,
) -> awesomeversion.AwesomeVersion:
    assert version.major is not None
    assert version.minor is not None
    assert version.patch is not None
    parts = [int(version.major), int(version.minor), int(version.patch)]
    zeroes = next(
        (i for i, v in enumerate(parts) if v != 0),
        len(parts) - 1,
    )
    i = min(bump - 1 + zeroes, len(parts) - 1)
    parts[i] += 1
    parts[i + 1 :] = [0 for _ in parts[i + 1 :]]
    return awesomeversion.AwesomeVersion(
        ".".join(str(p) for p in parts),
        ensure_strategy=awesomeversion.AwesomeVersionStrategy.SEMVER,
    )


def _create_git_tag(
    head: str,
    version: awesomeversion.AwesomeVersion,
    changelog: str,
) -> None:
    tagname = f"v{version}"
    logger.info("Creating git tag %s", tagname)
    with tempfile.TemporaryDirectory() as tmpdir:
        clpath = pathlib.Path(tmpdir) / "changelog.txt"
        clpath.write_text(changelog, encoding="utf-8")
        try:
            subprocess.check_call(
                [
                    "git",
                    "tag",
                    "--edit",
                    "--cleanup=verbatim",
                    "--sign",
                    f"-F{clpath}",
                    f"v{version}",
                    head,
                ]
            )
        except subprocess.CalledProcessError as e:
            raise SystemExit(
                f"Failed to create tag: git exited with code {e.returncode}"
            ) from None


def _read_tag_message(version: awesomeversion.AwesomeVersion) -> str:
    contents = _exec("git", "tag", "-l", "--format=%(contents)", f"v{version}")

    sig_start = contents.find("\n-----BEGIN PGP SIGNATURE-----\n\n")
    if sig_start < 0:
        logger.error("Did not find PGP signature in tag contents")
    else:
        contents = contents[:sig_start]

    return contents.strip()


def _copy_to_clipboard(text: str) -> None:
    utftext = text.encode("utf-8")
    b64text = base64.standard_b64encode(utftext).decode("ascii")
    escape = f"\x1b]52;;{b64text}\x1b\\"

    for stream in (sys.stdout, sys.stderr):
        if stream.isatty():
            logger.debug("Found a tty at fd %d", stream.fileno())
            stream.write(escape)
            stream.flush()
            logger.info("Changelog copied to clipboard")
            return

    if sys.stdin.isatty():
        logger.debug("Found a tty at fd %d", sys.stdin.fileno())
        with open(sys.stdin.fileno(), "w") as stream:
            stream.write(escape)
        logger.info("Changelog copied to clipboard")
        return


def _exec(exe: str, /, *args: str, **kw: t.Any) -> str:
    """Execute a command and return its stdout as string."""
    cmd = (exe, *args)
    logger.debug("exec: %r", cmd)
    return subprocess.check_output(cmd, encoding="utf-8", **kw).strip()


if __name__ == "__main__":
    _main()
