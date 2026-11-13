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

"""Guard against version drift: ``pacsifier/info.py`` is the single source."""

import glob
import os
import re

import pytest

from pacsifier.info import __version__

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WRAPPERS = sorted(glob.glob(os.path.join(ROOT, "scripts", "docker_*")))


def test_docker_wrappers_found():
    assert WRAPPERS, "no scripts/docker_* wrappers found"


@pytest.mark.parametrize("path", WRAPPERS, ids=os.path.basename)
def test_docker_wrapper_version_matches_info(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    versions = re.findall(r'^PACSIFIER_VERSION="([^"]*)"', content, re.MULTILINE)
    assert versions == [__version__], f"{os.path.basename(path)}: {versions}"
    # No other hardcoded image tag may remain in the wrapper.
    assert not re.search(r"pacsifier:\d+\.\d+\.\d+", content)
