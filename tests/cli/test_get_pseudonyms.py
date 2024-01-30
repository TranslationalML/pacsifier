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

"""Tests for the functions of the `pacsman.cli.get_pseudonyms` script."""

import os
import sys
import pytest


from pacsman.cli.get_pseudonyms import check_config_file_deid, convert_csv_to_deid_json


def test_check_config_file_deid():
    config_file = {
        "deid_URL": "https://deid.gpcr-project.org",
        "deid_token": "1234567890",
    }
    check_config_file_deid(config_file)

    config_file = {
        "deid_URL": "https://deid.gpcr-project.org",
        "deid_token": "1234567890",
        "dummy_key": "dummy_value",
    }
    with pytest.raises(ValueError):
        check_config_file_deid(config_file)

    config_file = {"deid_URL": "https://deid.gpcr-project.org"}
    with pytest.raises(ValueError):
        check_config_file_deid(config_file)


def test_convert_csv_to_deid_json(test_dir):
    queryfile = os.path.join(test_dir, "test_data", "query", "query_dicom.csv")
    project_name = "PACSMANCohort"
    json_new = convert_csv_to_deid_json(queryfile, project_name)
    print(json_new, file=sys.stderr)
    assert json_new == {
        "project": "PACSMANCohort",
        "PatientIDList": [{"PatientID": "PACSMAN1"}],
    }
    
    queryfile = os.path.join(test_dir, "test_data", "query", "query_file_invalid.csv")
    project_name = "PACSMANCohort"
    json_new = convert_csv_to_deid_json(queryfile, project_name)
    print(json_new, file=sys.stderr)
    assert json_new == {}
