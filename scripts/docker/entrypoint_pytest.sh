#!/bin/bash

# Copyright 2018-2024 University and University Hospital of Lausanne (UNIL-CHUV),
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

conda run -n pacsman_minimal pytest \
    --cov-config "/app/pacsman/.coveragerc" \
    --cov-report html:"/tests/report/cov_html" \
    --cov-report xml:"/tests/report/cov.xml" \
    --cov-report lcov:"/tests/report/cov.info" \
    --cov=pacsman \
    -s \
    "${@}"
