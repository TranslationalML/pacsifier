# Copyright 2018-2026 Lausanne University Hospital and University of Lausanne,
# Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Set the PACSIFIER version everywhere it is hard-coded.

``pacsifier/info.py`` is the single source of truth. The only other places that
carry the number are the ``PACSIFIER_VERSION`` line of each ``scripts/docker_*``
wrapper (they run on hosts without Python). This script updates both so they
cannot drift; ``tests/test_version_consistency.py`` fails if they do.

Usage: ``python utils/bump_version.py 1.2.0`` (or ``make bump-version V=1.2.0``)
"""

import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$")


def _rewrite(path: str, pattern: str, replacement: str) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        content = f.read()
    new, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly 1 match, found {count}")
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(new)


def main(argv: list) -> int:
    if len(argv) != 2 or not SEMVER.match(argv[1]):
        print("usage: bump_version.py X.Y.Z[-suffix]", file=sys.stderr)
        return 2
    version = argv[1]
    _rewrite(
        os.path.join(ROOT, "pacsifier", "info.py"),
        r'^__version__ = ".*"',
        f'__version__ = "{version}"',
    )
    wrappers = sorted(glob.glob(os.path.join(ROOT, "scripts", "docker_*")))
    for path in wrappers:
        _rewrite(path, r'^PACSIFIER_VERSION=".*"', f'PACSIFIER_VERSION="{version}"')
    print(f"Set version {version} in info.py and {len(wrappers)} wrappers.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
