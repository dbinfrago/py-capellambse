# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Main entry point for various CLI scripts around capellambse."""

import contextlib
import importlib
import importlib.resources as imr

import click

from . import _scripts


class LazyGroup(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        cmds = sorted(
            i.name.removesuffix(".py").replace("_", "-")
            for i in imr.files(_scripts).iterdir()
            if i.name.endswith(".py") and not i.name.startswith("_")
        )
        return super().list_commands(ctx) + cmds

    def get_command(
        self,
        ctx: click.Context,
        name: str,
    ) -> click.Command | None:
        with contextlib.suppress(ImportError):
            modname = name.replace("-", "_")
            cmd = importlib.import_module(
                f"{_scripts.__name__}.{modname}"
            ).main
            assert isinstance(cmd, click.Command)
            cmd.name = name
            return cmd

        return super().get_command(ctx, name)


@click.group(cls=LazyGroup, no_args_is_help=True)
def main() -> None:
    pass


if __name__ == "__main__":
    main()
