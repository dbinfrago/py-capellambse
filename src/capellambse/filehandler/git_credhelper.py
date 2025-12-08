#!/usr/bin/env python
# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0

import os
import sys


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(1)

    match sys.argv:
        case [] | [_]:
            raise SystemExit(1)
        case [_, "get"]:
            stream = sys.stdout
            if "GIT_USERNAME" in os.environ:
                stream.write(f"username={os.environ['GIT_USERNAME']}\n")
            if "GIT_PASSWORD" in os.environ:
                if stream.isatty():
                    stream.write("password=*** redacted ***\n")
                else:
                    stream.write(f"password={os.environ['GIT_PASSWORD']}\n")


if __name__ == "__main__":
    main()
