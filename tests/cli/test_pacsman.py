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

"""Tests for the functions of the `pacsman.cli.pacsman` script."""

from glob import glob
import json
import os
from pandas import read_csv
import pytest
from functools import reduce
import string
from hypothesis import given, example
from hypothesis.strategies import text

from pacsman.cli import (
    readLineByLine,
    parse_findscu_dump_file,
    check_query_table_allowed_filters,
    parse_query_table,
    process_person_names,
    generate_new_folder_name,
    add_or_retrieve_name,
)
from pacsman.cli.pacsman import retrieve_dicoms_using_table


def test_process_findscu_dump_file(test_dir):
    res = [
        {
            "SeriesInstanceUID": "1.2.840.114358.359.1.20171101170336.3712639202739",
            "StudyDate": "20171001",
            "SeriesDescription": "4metas24Gy_PTV18Gy_68min-RTDOSE",
            "PatientBirthDate": "19640101",
            "ProtocolName": "",
            "SeriesNumber": "",
            "ImageType": "",
            "StudyTime": "114557",
            "PatientID": "dummyid",
            "DeviceSerialNumber": "",
            "StudyDescription": "",
            "StudyInstanceUID": "1.2.826.0.1.3680043.2.146.2.20.3171184.1700225197.0",
            "PatientName": "dummyname",
            "AccessionNumber": "",
            "Modality": "",
        },
        {
            "SeriesInstanceUID": "1.2.840.231122.1230.23181726456172.1",
            "StudyDate": "20171001",
            "SeriesDescription": "4metas24Gy_PTV18Gy_68min",
            "PatientBirthDate": "19640101",
            "ProtocolName": "",
            "SeriesNumber": "",
            "ImageType": "",
            "StudyTime": "114557",
            "PatientID": "dummyid",
            "DeviceSerialNumber": "",
            "StudyDescription": "",
            "StudyInstanceUID": "1.2.826.0.1.3680043.2.146.2.20.3171184.170022.232193921818771717",
            "PatientName": "dummyname",
            "AccessionNumber": "",
            "Modality": "",
        },
    ]

    # Testing all the dictionaries in the list are identical.
    dict_list = parse_findscu_dump_file(
        filename=os.path.join(
            test_dir, "test_data", "dump", "findscu_dump_file_example.txt"
        )
    )
    for i, dict_ in enumerate(dict_list):
        shared_items = {
            k: res[i][k] for k in res[i] if k in dict_ and res[i][k] == dict_[k]
        }
        assert len(shared_items) == len(res[i])


def test_check_table(test_dir):
    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_file_invalid.csv")
    ).fillna("")
    with pytest.raises(ValueError):
        check_query_table_allowed_filters(table)

    valid_table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_file_valid.csv")
    ).fillna("")
    assert check_query_table_allowed_filters(valid_table) == None


def test_parse_table(test_dir):
    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_file_valid.csv")
    )
    parsed_table = parse_query_table(table)

    expected = [
        {
            "new_ids": "",
            "StudyDescription": "",
            "DeviceSerialNumber": "",
            "AcquisitionDate": "",
            "StudyInstanceUID": "",
            "SeriesDescription": "",
            "PatientID": 125,
            "StudyTime": "",
            "ImageType": "",
            "AccessionNumber": "",
            "StudyDate": 20170814,
            "Modality": "",
            "SeriesNumber": "",
            "ProtocolName": "",
            "PatientBirthDate": "",
            "SeriesInstanceUID": "",
            "PatientName": "",
        }
    ]

    for i, dict_ in enumerate(parsed_table):
        shared_items = {
            k: expected[i][k]
            for k in expected[i]
            if k in dict_ and expected[i][k] == dict_[k]
        }
        assert len(shared_items) == len(expected[i])


def test_read_line_by_line(test_dir):
    lines = list(
        readLineByLine(os.path.join(test_dir, "test_data", "dump", "findscu_dump_file_example.txt"))
    )[:4]
    assert lines == [
        "I: Requesting Association",
        "I: Association Accepted (Max Send PDV: 32756)",
        "I: Sending Find Request (MsgID 1)",
        "I: Request Identifiers:",
    ]


def test_process_name():
    assert process_person_names("Obi-Wan Kenobi") == "*KENOBI"
    assert process_person_names("") == ""


@given(s=text())
@example(s="Obi-Wan Kenobi")
def test_check_date_input(s):
    processed = process_person_names(s)
    if s == "":
        assert processed == ""
    else:
        assert process_person_names(s) == "*" + s.split(" ")[-1].upper()


def test_generate_new_folder_name():
    assert len(generate_new_folder_name()) <= 8
    name = list(generate_new_folder_name())
    assert reduce(
        lambda x, y: x and y,
        [(letter in (string.ascii_uppercase + string.digits)) for letter in name],
    )
    assert generate_new_folder_name(names=["".join(name)]) != "".join(name)


def test_add_or_retrieve_name():
    folder_name, old_2_new = add_or_retrieve_name("Hello", {})
    assert add_or_retrieve_name("Hello", {"Hello": folder_name}) == (
        folder_name,
        old_2_new,
    )


def test_retrieve_dicoms_using_table(test_dir):
    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_dicom.csv"),
        dtype=str
    ).fillna("")
    config_path = os.path.join("/tests/config/config.json")

    with open(config_path) as f:
        parameters = json.load(f)

    out_directory = os.path.join(test_dir, "tmp", "test_set")

    # Test retrieve DICOM series

    # retrieve_dicoms_using_table(table, parameters, out_directory, False, False)
    # assert glob("./test_set/sub-*/ses-*/*/*") == []

    # retrieve_dicoms_using_table(table, parameters, out_directory, False, True)
    # assert glob("./test_set/sub-*/ses-*/*/*") == []

    retrieve_dicoms_using_table(table, parameters, out_directory, True, True, False)

    # Assert the first six files of the list are correct
    output_files = glob(
        os.path.join(test_dir, "tmp", "test_set", "sub-*/ses-*/*/*")
    )
    known_files_dir = os.path.join(test_dir, "tmp", "test_set", "sub-PACSMAN1", "ses-20231016")
    known_files_dir = os.path.join(known_files_dir, "00000-No_series_description")
    known_filenames = [
        "MR.1.2.826.0.1.3680043.8.498.10078350936423615213975808998561561261",
        "MR.1.2.826.0.1.3680043.8.498.10079063413960953608145500849488605317",
        "MR.1.2.826.0.1.3680043.8.498.10254832511701611336169372822417032099",
        "MR.1.2.826.0.1.3680043.8.498.10297714540640569882794200001611356979",
        "MR.1.2.826.0.1.3680043.8.498.10299592168011030062855381217267705761",
        "MR.1.2.826.0.1.3680043.8.498.10773050947549757012436832094131147157",
    ]
    known_files = [os.path.join(known_files_dir, file) for file in known_filenames]
    assert sorted(output_files)[:6] == sorted(known_files)[:6]


def test_check_output_info():
    pass

    # pacsman.main(["--info", "--queryfile test.csv", "--out_directory ./tests/test_set",  "--config ./files/config.json"])
    # subjects = glob("./test_set/*")
    # sessions = glob("./test_set/sub-*/ses-*")
    # csv_files = glob("./test_set/sub-*/ses-*/*.csv")

    # assert subjects == ['./test_set/sub-XXX']
    # assert sessions == ['./test_set/sub-XXX/ses-YYY', './test_set/sub-XXX/ses-ZZZ']
    # assert csv_files == ['./test_set/sub-XXX/ses-YYY/foo.csv', ... ]
