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
import json
import pytest
import tempfile
import shutil
import csv
import pandas as pd
from unittest import mock

from pacsifier.cli.get_pseudonyms import (
    DEID_REQUEST_TIMEOUT,
    check_config_file_deid,
    check_queryfile_content,
    convert_csv_to_deid_json,
    generate_csv_with_pseudonyms_and_day_shifts,
    get_deid_day_shifts,
    get_deid_pseudonyms,
    get_deid_tls_verify,
    split_deid_query_json_in_batch
)

@pytest.fixture
def test_dir():
    # Create a temporary directory for the test
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after the test
    shutil.rmtree(temp_dir)


def test_convert_csv_with_utf8_sig_encoding(tmpdir):
    queryfile = os.path.join(tmpdir, "query.csv")

    # Write the CSV with UTF-8-sig encoding to simulate a file with BOM
    with open(queryfile, "w", encoding="UTF-8-sig") as csvfile:
        csvfile.write("PatientID,AccessionNumber\n")
        csvfile.write("123,AAA\n")
        csvfile.write("432,BBB\n")

    project_name = "TestProject"
    json_new = convert_csv_to_deid_json(queryfile, project_name)

    assert json_new == {
        "project": "TestProject",
        "PatientIDList": [
            {"PatientID": "123"},
            {"PatientID": "432"}
        ],
    }


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


@pytest.mark.parametrize("verify", [True, False, "/path/to/ca_bundle.pem"])
def test_check_config_file_deid_optional_verify(verify):
    config_file = {
        "deid_URL": "https://dummy.url.example",
        "deid_token": "1234567890",
        "deid_verify": verify,
    }
    check_config_file_deid(config_file)


def test_check_config_file_deid_invalid_verify():
    config_file = {
        "deid_URL": "https://dummy.url.example",
        "deid_token": "1234567890",
        "deid_verify": 1.5,
    }
    with pytest.raises(ValueError):
        check_config_file_deid(config_file)


def test_get_deid_tls_verify():
    base = {"deid_URL": "https://dummy.url.example", "deid_token": "1234567890"}
    assert get_deid_tls_verify(base) is True
    assert get_deid_tls_verify({**base, "deid_verify": "/ca.pem"}) == "/ca.pem"
    with pytest.warns(UserWarning, match="TLS certificate verification is disabled"):
        assert get_deid_tls_verify({**base, "deid_verify": False}) is False


@mock.patch("pacsifier.cli.get_pseudonyms.requests.post")
def test_get_deid_requests_verify_tls_by_default(mock_post):
    params = {"deid_URL": "https://dummy.url.example", "deid_token": "1234567890"}
    mock_post.return_value = mock.Mock(text='{"P1": "1"}')

    get_deid_pseudonyms(params, {"PatientIDList": []})
    get_deid_day_shifts(params, {"PatientIDList": []})

    assert mock_post.call_count == 2
    for call in mock_post.call_args_list:
        assert call.kwargs["verify"] is True
        assert call.kwargs["timeout"] == DEID_REQUEST_TIMEOUT


@mock.patch("pacsifier.cli.get_pseudonyms.requests.post")
def test_get_deid_requests_custom_ca_bundle(mock_post):
    params = {
        "deid_URL": "https://dummy.url.example",
        "deid_token": "1234567890",
        "deid_verify": "/ca.pem",
    }
    mock_post.return_value = mock.Mock(text='{"P1": "1"}')

    get_deid_pseudonyms(params, {"PatientIDList": []})
    get_deid_day_shifts(params, {"PatientIDList": []})

    for call in mock_post.call_args_list:
        assert call.kwargs["verify"] == "/ca.pem"


def test_convert_csv_to_deid_json(test_dir):
    # Copy the source file into the temporary directory
    src_queryfile = os.path.join(os.path.dirname(__file__), "../test_data/query/query_dicom.csv")
    queryfile = os.path.join(test_dir, "query_dicom.csv")
    os.makedirs(os.path.dirname(queryfile), exist_ok=True)
    shutil.copy(src_queryfile, queryfile)

    # Test with a valid file
    project_name = "PACSIFIERCohort"
    json_new = convert_csv_to_deid_json(queryfile, project_name)
    assert json_new == {
        "project": "PACSIFIERCohort",
        "PatientIDList": [{"PatientID": "PACSMAN1"}],
    }

    # Test with an invalid file
    invalid_queryfile = os.path.join(test_dir, "query_file_invalid.csv")
    with open(invalid_queryfile, "w", encoding="utf-8") as f:
        f.write("InvalidHeader\n")
    json_new = convert_csv_to_deid_json(invalid_queryfile, project_name)
    assert json_new == {}


def test_check_queryfile_content(test_dir):
    # Copy the source file into the temporary directory
    src_queryfile = os.path.join(os.path.dirname(__file__), "../test_data/query/query_dicom.csv")
    queryfile = os.path.join(test_dir, "query_dicom.csv")
    os.makedirs(os.path.dirname(queryfile), exist_ok=True)
    shutil.copy(src_queryfile, queryfile)

    # Test with a valid file
    check_queryfile_content(queryfile)

    # Test with an invalid file
    invalid_queryfile = os.path.join(test_dir, "query_file_invalid.csv")
    with open(invalid_queryfile, "w", encoding="utf-8") as f:
        f.write("InvalidHeader\n")
    with pytest.raises(ValueError):
        check_queryfile_content(invalid_queryfile)


def test_custom_get_pseudonyms_script_with_shift(script_runner, test_dir):
    # Create the required directory and file
    mapping_dir = os.path.join(test_dir, "test_data", "pseudo_mapping")
    os.makedirs(mapping_dir, exist_ok=True)
    mapping_file = os.path.join(mapping_dir, "pseudo_mapping.csv")
    with open(mapping_file, "w", encoding="utf-8") as f:
        f.write("OldID,NewID\n")
        f.write("1234,P0001\n")
        f.write("87262,P0002\n")

    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Run the script
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            mapping_file,
            "--shift-days",
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    assert ret.success
    # Check that the new_ids and day_shift files are created
    new_ids_path = os.path.join(output_dir, f"new_ids_{project_name}.json")
    day_shift_path = os.path.join(output_dir, f"day_shift_{project_name}.json")
    assert os.path.exists(new_ids_path)
    assert os.path.exists(day_shift_path)
    # Check that the content of the new_ids file is correct
    assert json.load(open(new_ids_path, encoding='utf-8')) == {"1234": "P0001", "87262": "P0002"}
    # Check that the content of the day shifts in the day_shift file are within the range -30 to 30
    day_shifts = json.load(open(day_shift_path, encoding='utf-8'))
    assert all(-30 <= shift <= 30 for shift in day_shifts.values())

def test_custom_get_pseudonyms_script_no_shift(script_runner, test_dir):
    # Create the required directory and file
    mapping_dir = os.path.join(test_dir, "test_data", "pseudo_mapping")
    os.makedirs(mapping_dir, exist_ok=True)
    mapping_file = os.path.join(mapping_dir, "pseudo_mapping.csv")
    with open(mapping_file, "w", encoding="utf-8") as f:
        f.write("OldID,NewID\n")
        f.write("1234,P0001\n")
        f.write("87262,P0002\n")

    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms")
    project_name = "PACSIFIERCohort"

    # Debugging: Print paths
    print(f"Mapping file path: {mapping_file}")
    print(f"Output directory: {output_dir}")

    # Check that the script runs successfully when the flag --shift-days is not set
    ret = script_runner.run(
        [
            "pacsifier-get-pseudonyms",
            "-m",
            "custom",
            "-mf",
            mapping_file,
            "--project_name",
            project_name,
            "-v",
            "-d",
            output_dir,
        ]
    )
    assert ret.success
    # Check that the day_shift file is created
    day_shift_path = os.path.join(output_dir, f"day_shift_{project_name}.json")
    print(f"Day shift file path: {day_shift_path}")
    assert os.path.exists(day_shift_path)
    # Check that the content of the day_shift file is correct
    assert json.load(open(day_shift_path, encoding='utf-8')) == {"1234": 0, "87262": 0}

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
            os.path.join(
                test_dir, "test_data", "pseudo_mapping",
                "pseudo_mapping_not_existing.csv"
            ),
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


@mock.patch("pacsifier.cli.get_pseudonyms.requests.post")
@mock.patch("pacsifier.cli.get_pseudonyms.open", create=True)
def test_generate_csv_with_pseudonyms_and_day_shifts(mock_open, mock_post, test_dir):
    # Define mock responses for the API
    mock_pseudonym_response = {"sub-125": "P0001"}
    mock_day_shift_response = {"sub-125": -5}
    mock_post.side_effect = [
        mock.Mock(text=json.dumps(mock_pseudonym_response)),
        mock.Mock(text=json.dumps(mock_day_shift_response)),
    ]

    # Create the required query file
    query_dir = os.path.join(test_dir, "test_data", "query")
    os.makedirs(query_dir, exist_ok=True)
    queryfile = os.path.join(query_dir, "query_file_valid.csv")
    with open(queryfile, "w", encoding="utf-8") as f:
        f.write("PatientID,StudyDate\n")
        f.write("125,20170814\n")

    # Set up the output directory
    output_dir = os.path.join(test_dir, "tmp", "test_get_pseudonyms", "logs")
    os.makedirs(output_dir, exist_ok=True)

    # Call the function
    pseudonyms = mock_pseudonym_response
    day_shifts = mock_day_shift_response
    generate_csv_with_pseudonyms_and_day_shifts(queryfile, pseudonyms, day_shifts, output_dir)

    # Check the output CSV file
    expected_csv_path = os.path.join(output_dir, "log_get_pseudonyms.csv")
    assert os.path.exists(expected_csv_path)

    # Read and check the content of the CSV file
    generated_csv = pd.read_csv(expected_csv_path, dtype={"PatientID": str, "StudyDate": str})
    assert list(generated_csv.columns) == ["PatientID", "StudyDate", "NewPseudonym", "DayShift"]
    assert generated_csv["PatientID"].tolist() == ["125"]
    assert generated_csv["StudyDate"].tolist() == ["20170814"]
    assert generated_csv["NewPseudonym"].tolist() == ["P0001"]
    assert generated_csv["DayShift"].tolist() == [-5]

def test_split_deid_query_json_in_batch_empty_list():
    """Test splitting an empty patient list."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": []
    }
    batch_size = 500

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 0


def test_split_deid_query_json_in_batch_single_patient():
    """Test splitting a single patient."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": "123"}]
    }
    batch_size = 500

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 1
    assert batches[0]["project"] == "TestProject"
    assert batches[0]["PatientIDList"] == [{"PatientID": "123"}]


def test_split_deid_query_json_in_batch_exact_batch_size():
    """Test splitting when patient count equals batch size."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(500)]
    }
    batch_size = 500

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 1
    assert len(batches[0]["PatientIDList"]) == 500
    assert batches[0]["project"] == "TestProject"


def test_split_deid_query_json_in_batch_multiple_batches():
    """Test splitting into multiple batches."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(1200)]
    }
    batch_size = 500

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 3
    assert len(batches[0]["PatientIDList"]) == 500
    assert len(batches[1]["PatientIDList"]) == 500
    assert len(batches[2]["PatientIDList"]) == 200

    # Check that all batches have the correct project
    for batch in batches:
        assert batch["project"] == "TestProject"

    # Check that all patients are included
    all_patients = []
    for batch in batches:
        all_patients.extend(batch["PatientIDList"])
    assert len(all_patients) == 1200


def test_split_deid_query_json_in_batch_small_batch_size():
    """Test splitting with a small batch size."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(7)]
    }
    batch_size = 3

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 3
    assert len(batches[0]["PatientIDList"]) == 3
    assert len(batches[1]["PatientIDList"]) == 3
    assert len(batches[2]["PatientIDList"]) == 1


def test_split_deid_query_json_in_batch_preserves_patient_data():
    """Test that patient data is preserved correctly in batches."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [
            {"PatientID": "patient1", "extra_field": "value1"},
            {"PatientID": "patient2", "extra_field": "value2"},
            {"PatientID": "patient3", "extra_field": "value3"}
        ]
    }
    batch_size = 2

    batches = split_deid_query_json_in_batch(deid_query_json, batch_size)

    assert len(batches) == 2
    assert len(batches[0]["PatientIDList"]) == 2
    assert len(batches[1]["PatientIDList"]) == 1

    # Check that patient data is preserved
    assert batches[0]["PatientIDList"][0] == {
        "PatientID": "patient1", "extra_field": "value1"
    }
    assert batches[0]["PatientIDList"][1] == {
        "PatientID": "patient2", "extra_field": "value2"
    }
    assert batches[1]["PatientIDList"][0] == {
        "PatientID": "patient3", "extra_field": "value3"
    }


def test_generate_csv_with_pseudonyms_and_day_shifts_sub_prefix(test_dir):
    """Test that the 'sub-' prefix is correctly added to PatientIDs in the CSV generation."""
    # Create a temporary query file
    queryfile = os.path.join(test_dir, "tmp", "test_query.csv")
    os.makedirs(os.path.dirname(queryfile), exist_ok=True)

    with open(queryfile, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write("PatientID,StudyDate\n")
        csvfile.write("123,20170814\n")
        csvfile.write("456,20170815\n")

    # Define pseudonyms and day shifts with 'sub-' prefix
    pseudonyms = {
        "sub-123": "P0001",
        "sub-456": "P0002"
    }
    day_shifts = {
        "sub-123": -5,
        "sub-456": 10
    }

    output_dir = os.path.join(test_dir, "tmp", "test_output")
    os.makedirs(output_dir, exist_ok=True)

    # Call the function
    generate_csv_with_pseudonyms_and_day_shifts(
        queryfile, pseudonyms, day_shifts, output_dir
    )

    # Check the output CSV file
    expected_csv_path = os.path.join(output_dir, "log_get_pseudonyms.csv")
    assert os.path.exists(expected_csv_path)

    # Read and check the content
    generated_csv = pd.read_csv(
        expected_csv_path, dtype={'PatientID': str, 'StudyDate': str}
    )

    assert list(generated_csv.columns) == [
        "PatientID", "StudyDate", "NewPseudonym", "DayShift"
    ]
    assert generated_csv["PatientID"].tolist() == ["123", "456"]
    assert generated_csv["NewPseudonym"].tolist() == ["P0001", "P0002"]
    assert generated_csv["DayShift"].tolist() == [-5, 10]


@mock.patch("pacsifier.cli.get_pseudonyms.get_deid_pseudonyms")
@mock.patch("pacsifier.cli.get_pseudonyms.get_deid_day_shifts")
def test_main_batching_functionality(
    mock_get_day_shifts, mock_get_pseudonyms, script_runner, test_dir
):
    """Test that the main function correctly handles batching for large patient lists."""
    # Create a large query file with 1200 patients
    queryfile = os.path.join(test_dir, "tmp", "large_query.csv")
    os.makedirs(os.path.dirname(queryfile), exist_ok=True)

    with open(queryfile, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write("PatientID,StudyDate\n")
        for i in range(1200):
            csvfile.write(f"patient{i},20170814\n")

    # Create a config file
    configfile = os.path.join(test_dir, "tmp", "config.json")
    with open(configfile, 'w', encoding='utf-8') as f:
        json.dump({
            "deid_URL": "https://test.example.com",
            "deid_token": "test_token"
        }, f)

    # Mock the API responses
    def mock_pseudonym_response(_deid_parameters, batch):
        # Return a response based on the batch size
        response = {}
        for patient in batch["PatientIDList"]:
            response[patient["PatientID"]] = f"P{patient['PatientID']}"
        return json.dumps(response)

    def mock_day_shift_response(_deid_parameters, batch):
        # Return a response based on the batch size
        response = {}
        for patient in batch["PatientIDList"]:
            response[patient["PatientID"]] = 0
        return json.dumps(response)

    mock_get_pseudonyms.side_effect = mock_pseudonym_response
    mock_get_day_shifts.side_effect = mock_day_shift_response

    output_dir = os.path.join(test_dir, "tmp", "test_batching_output")
    project_name = "TestProject"

    # Run the script
    ret = script_runner.run([
        "pacsifier-get-pseudonyms",
        "-m", "de-id",
        "-c", configfile,
        "-q", queryfile,
        "--project_name", project_name,
        "-d", output_dir
    ])

    # Check that the script runs successfully
    assert ret.success

    # Check that the API was called the correct number of times
    # (3 batches for pseudonyms + 3 for day shifts)
    assert mock_get_pseudonyms.call_count == 3
    assert mock_get_day_shifts.call_count == 3

    # Check that output files are created
    assert os.path.exists(
        os.path.join(output_dir, f"new_ids_{project_name}.json")
    )
    assert os.path.exists(
        os.path.join(output_dir, f"day_shift_{project_name}.json")
    )
    assert os.path.exists(os.path.join(output_dir, "log_get_pseudonyms.csv"))

    # Check that the CSV contains all 1200 patients
    csv_path = os.path.join(output_dir, "log_get_pseudonyms.csv")
    generated_csv = pd.read_csv(csv_path, dtype={'PatientID': str})
    assert len(generated_csv) == 1200


def test_split_deid_query_json_in_batch_type_hints():
    """Test that the function works with proper type hints."""
    from typing import Dict, List, Any

    # This test ensures the function signature is compatible with type hints
    deid_query_json: Dict[str, Any] = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": "123"}]
    }
    batch_size: int = 500

    batches: List[Dict[str, Any]] = split_deid_query_json_in_batch(
        deid_query_json, batch_size
    )

    assert isinstance(batches, list)
    assert len(batches) == 1
    assert isinstance(batches[0], dict)
    assert "project" in batches[0]
    assert "PatientIDList" in batches[0]


def test_split_deid_query_json_in_batch_different_sizes():
    """Test splitting with various batch sizes."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(10)]
    }

    # Test batch size 1
    batches_1 = split_deid_query_json_in_batch(deid_query_json, 1)
    assert len(batches_1) == 10
    for batch in batches_1:
        assert len(batch["PatientIDList"]) == 1
        assert batch["project"] == "TestProject"

    # Test batch size 3
    batches_3 = split_deid_query_json_in_batch(deid_query_json, 3)
    assert len(batches_3) == 4  # 3 + 3 + 3 + 1
    assert len(batches_3[0]["PatientIDList"]) == 3
    assert len(batches_3[1]["PatientIDList"]) == 3
    assert len(batches_3[2]["PatientIDList"]) == 3
    assert len(batches_3[3]["PatientIDList"]) == 1

    # Test batch size 5
    batches_5 = split_deid_query_json_in_batch(deid_query_json, 5)
    assert len(batches_5) == 2  # 5 + 5
    assert len(batches_5[0]["PatientIDList"]) == 5
    assert len(batches_5[1]["PatientIDList"]) == 5

    # Test batch size larger than total patients
    batches_20 = split_deid_query_json_in_batch(deid_query_json, 20)
    assert len(batches_20) == 1
    assert len(batches_20[0]["PatientIDList"]) == 10


def test_split_deid_query_json_in_batch_edge_cases():
    """Test edge cases for batch splitting."""
    # Test with exactly 500 patients (default batch size)
    deid_query_json_500 = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(500)]
    }
    batches_500 = split_deid_query_json_in_batch(deid_query_json_500, 500)
    assert len(batches_500) == 1
    assert len(batches_500[0]["PatientIDList"]) == 500

    # Test with 501 patients (just over default batch size)
    deid_query_json_501 = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(501)]
    }
    batches_501 = split_deid_query_json_in_batch(deid_query_json_501, 500)
    assert len(batches_501) == 2
    assert len(batches_501[0]["PatientIDList"]) == 500
    assert len(batches_501[1]["PatientIDList"]) == 1

    # Test with 1000 patients (exactly 2 batches)
    deid_query_json_1000 = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(1000)]
    }
    batches_1000 = split_deid_query_json_in_batch(deid_query_json_1000, 500)
    assert len(batches_1000) == 2
    assert len(batches_1000[0]["PatientIDList"]) == 500
    assert len(batches_1000[1]["PatientIDList"]) == 500


def test_split_deid_query_json_in_batch_zero_batch_size():
    """Test behavior with zero batch size (should handle gracefully)."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": "123"}]
    }

    # With batch size 0, should create one batch with all patients
    batches = split_deid_query_json_in_batch(deid_query_json, 0)
    assert len(batches) == 1
    assert len(batches[0]["PatientIDList"]) == 1


def test_split_deid_query_json_in_batch_negative_batch_size():
    """Test behavior with negative batch size (should handle gracefully)."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": "123"}]
    }

    # With negative batch size, should create one batch with all patients
    batches = split_deid_query_json_in_batch(deid_query_json, -1)
    assert len(batches) == 1
    assert len(batches[0]["PatientIDList"]) == 1


def test_split_deid_query_json_in_batch_default_batch_size():
    """Test that the default batch size of 500 works correctly."""
    deid_query_json = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": str(i)} for i in range(750)]
    }

    # Test with default batch size (500)
    batches_default = split_deid_query_json_in_batch(deid_query_json)
    assert len(batches_default) == 2
    assert len(batches_default[0]["PatientIDList"]) == 500
    assert len(batches_default[1]["PatientIDList"]) == 250

    # Test with explicit batch size 500 (should be same result)
    batches_explicit = split_deid_query_json_in_batch(deid_query_json, 500)
    assert len(batches_explicit) == 2
    assert len(batches_explicit[0]["PatientIDList"]) == 500
    assert len(batches_explicit[1]["PatientIDList"]) == 250

    # Verify both results are identical
    assert batches_default == batches_explicit


def test_split_deid_query_json_in_batch_type_annotations():
    """Test that the function accepts properly typed arguments."""
    from typing import Dict, List, Any

    # Test with properly typed arguments
    deid_query_json: Dict[str, Any] = {
        "project": "TestProject",
        "PatientIDList": [{"PatientID": "123"}]
    }
    batch_size: int = 500

    # This should work without type errors
    batches: List[Dict[str, Any]] = split_deid_query_json_in_batch(
        deid_query_json, batch_size
    )

    assert isinstance(batches, list)
    assert len(batches) == 1
    assert isinstance(batches[0], dict)
    assert "project" in batches[0]
    assert "PatientIDList" in batches[0]
