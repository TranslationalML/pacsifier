# Copyright 2018-2024 Lausanne University Hospital and University of Lausanne,
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

"""Tests for the functions of the `pacsifier.cli.get_pseudonyms` script."""

import os
import shutil
import sys
import json
import pytest


from pacsifier.cli.get_pseudonyms import (
    check_config_file_deid,
    check_queryfile_content,
    convert_csv_to_deid_json,
)


def test_check_config_file_deid():
    config_file = {
        "deid_URL": "https://dummy.url.example",
        "deid_token": "1234567890",
    }
    check_config_file_deid(config_file)

    config_file = {
        "deid_URL": "https://dummy.url.example",
        "deid_token": "1234567890",
        "dummy_key": "dummy_value",
    }
    with pytest.raises(ValueError):
        check_config_file_deid(config_file)

    config_file = {"deid_URL": "https://dummy.url.example"}
    with pytest.raises(ValueError):
        check_config_file_deid(config_file)


def test_convert_csv_to_deid_json(test_dir):
    queryfile = os.path.join(test_dir, "test_data", "query", "query_dicom.csv")
    project_name = "PACSIFIERCohort"
    json_new = convert_csv_to_deid_json(queryfile, project_name)
    assert json_new == {
        "project": "PACSIFIERCohort",
        "PatientIDList": [{"PatientID": "PACSMAN1"}],
    }

    queryfile = os.path.join(test_dir, "test_data", "query", "query_file_invalid.csv")
    project_name = "PACSIFIERCohort"
    json_new = convert_csv_to_deid_json(queryfile, project_name)
    assert json_new == {}


def test_check_queryfile_content(test_dir):
    queryfile = os.path.join(test_dir, "test_data", "query", "query_dicom.csv")
    check_queryfile_content(queryfile)

    queryfile = os.path.join(test_dir, "test_data", "query", "query_file_invalid.csv")
    with pytest.raises(ValueError):
        check_queryfile_content(queryfile)


def test_custom_get_pseudonyms_script_with_shift(script_runner, test_dir):
    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Check that the script runs successfully when the flag --shift-days is set
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            os.path.join(test_dir, "test_data", "pseudo_mapping", "pseudo_mapping.csv"),
            "--shift-days",
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    # Check that the script runs successfully
    assert ret.success
    # Check that the new_ids and day_shift files are created
    assert os.path.exists(os.path.join(output_dir, f"new_ids_{project_name}.json"))
    assert os.path.exists(os.path.join(output_dir, f"day_shift_{project_name}.json"))
    # Check that the content of the new_ids file is correct
    assert json.load(
        open(os.path.join(output_dir, f"new_ids_{project_name}.json"))
    ) == {"sub-1234": "P0001", "sub-87262": "P0002"}
    # Check that the content of the day shifts in the day_shift file are not all 0
    assert json.load(
        open(os.path.join(output_dir, f"day_shift_{project_name}.json"))
    ) != {"sub-1234": 0, "sub-87262": 0}


def test_custom_get_pseudonyms_script_no_shift(script_runner, test_dir):
    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Check that the script runs successfully when the flag --shift-days is not set
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            os.path.join(test_dir, "test_data", "pseudo_mapping", "pseudo_mapping.csv"),
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    # Check that the script runs successfully
    assert ret.success
    # Check that the day_shift files is created
    assert os.path.exists(os.path.join(output_dir, f"day_shift_{project_name}.json"))
    # Check that the content of the day_shift file is correct
    assert json.load(
        open(os.path.join(output_dir, f"day_shift_{project_name}.json"))
    ) == {"sub-1234": 0, "sub-87262": 0}


def test_failure_custom_get_pseudonyms_script_no_mapping(script_runner, test_dir):
    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Check that the script fails to run if the mapping file is not found
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            os.path.join(test_dir, "test_data", "pseudo_mapping", "pseudo_mapping_not_existing.csv"),
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    # Check that the script fails
    assert not ret.success


def test_failure_custom_get_pseudonyms_script_empty_cell(script_runner, test_dir):
    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Check that the script fails to run if the mapping file contains an empty cell
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            os.path.join(test_dir, "test_data", "pseudo_mapping", "pseudo_mapping_empty_cell.csv"),
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    # Check that the script fails
    assert not ret.success
