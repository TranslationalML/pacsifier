#!/bin/bash

# Copyright (C) 2018-2024, University Hospital Center and University of Lausanne (UNIL-CHUV),
# Switzerland & Contributors, All rights reserved.
# This software is distributed under the open-source Apache 2.0 license.

conda run -n pacsman_minimal pytest \
    --cov-config "/app/pacsman/.coveragerc" \
    --cov-report html:"/tests/report/cov_html" \
    --cov-report xml:"/tests/report/cov.xml" \
    --cov-report lcov:"/tests/report/cov.info" \
    --cov=pacsman \
    -s \
    "${@}"
