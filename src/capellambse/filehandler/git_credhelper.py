#!/usr/bin/env python
# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0

import os
import sys


def main():
    if len(sys.argv) < 2:
        raise SystemExit(1)

    match sys.argv:
        case [] | [_]:
            raise SystemExit(1)
        case [_, "get"]:
            if "GIT_USERNAME" in os.environ:
                print(f"username={os.environ['GIT_USERNAME']}")
            if "GIT_PASSWORD" in os.environ:
                print(f"password={os.environ['GIT_PASSWORD']}")


if __name__ == "__main__":
    main()
