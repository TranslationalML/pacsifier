#!/bin/bash

# Copyright (C) 2018-2023, University Hospital Center and University of Lausanne (UNIL-CHUV)
# and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

conda run -n pacsman_minimal pytest \
    --cov-config "/app/pacsman/.coveragerc" \
    --cov-report html:"/test/report/cov_html" \
    --cov-report xml:"/test/report/cov.xml" \
    --cov-report lcov:"/test/report/cov.info" \
    --cov=pacsman \
    -s \
    "${@}"
