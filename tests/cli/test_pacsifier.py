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

"""Tests for the functions of the `pacsifier.cli.pacsifier` script."""

from glob import glob
import json
import os
from pandas import read_csv, DataFrame
import pytest
from functools import reduce
import string
import shutil
from hypothesis import given, example
from hypothesis.strategies import text
from pathlib import Path

from pacsifier.cli import (
    readLineByLine,
    parse_findscu_dump_file,
    parse_findscu_count_dump_file,
    check_query_table_allowed_filters,
    parse_query_table,
    process_person_names,
    generate_new_folder_name,
    add_or_retrieve_name,
    count_dicoms_using_table,
    retrieve_dicoms_using_table,
    upload_dicoms,
    ALLOWED_FILTERS,
)
import pacsifier.cli.pacsifier as pacsifier_cli


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


def test_parse_findscu_count_dump_file(tmp_path):
    dump_content = "\n".join(
        [
            "I: Requesting Association",
            "------------",
            "(0010,0020) LO [PACSMAN1]",
            "(0020,000d) UI [1.2.3]",
            "(0020,1206) IS [2]",
            "(0020,1208) IS [42]",
            "------------",
            "(0010,0020) LO [PACSMAN1]",
            "(0020,000d) UI [1.2.4]",
            "(0020,1206) IS [3]",
            "(0020,1208) IS [84]",
            "Releasing Association",
        ]
    )
    dump_file = tmp_path / "count_dump.txt"
    dump_file.write_text(dump_content, encoding="utf-8")

    parsed = parse_findscu_count_dump_file(str(dump_file))
    assert len(parsed) == 2
    assert parsed[0]["PatientID"] == "PACSMAN1"
    assert parsed[0]["NumberOfStudyRelatedSeries"] == "2"
    assert parsed[0]["NumberOfStudyRelatedInstances"] == "42"
    assert parsed[1]["StudyInstanceUID"] == "1.2.4"


def test_check_table(test_dir):
    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_file_invalid.csv")
    ).fillna("")
    with pytest.raises(ValueError):
        check_query_table_allowed_filters(table)

    valid_table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_file_valid.csv")
    ).fillna("")
    assert check_query_table_allowed_filters(valid_table) is None


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
        readLineByLine(
            os.path.join(test_dir, "test_data", "dump", "findscu_dump_file_example.txt")
        )
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


def test_invalid_retrieve_dicoms_using_table(test_dir):
    config_path = os.path.join(test_dir, "config", "config.json")
    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_dicom.csv"), dtype=str
    ).fillna("")
    out_directory = os.path.join(test_dir, "tmp", "test_set")

    with open(config_path) as f:
        parameters = json.load(f)

    invalid_parameters = parameters.copy()
    # Invalid server address to test the RuntimeError because of timeout
    invalid_parameters["server_address"] = "128.1.0.1"

    with pytest.raises(RuntimeError):
        retrieve_dicoms_using_table(
            table,
            invalid_parameters,
            out_directory,
            True,
            True,
            False,
        )


def test_retrieve_dicoms_using_table(test_dir):
    # Ensure output directory exists
    out_directory = os.path.join(test_dir, "tmp", "test_set")
    if os.path.exists(out_directory):
        shutil.rmtree(out_directory)  # Clear old files if needed
    os.makedirs(out_directory)  # Create fresh output directory

    table = read_csv(
        os.path.join(test_dir, "test_data", "query", "query_dicom.csv"), dtype=str
    ).fillna("")
    config_path = os.path.join(test_dir, "config", "config.json")
    with open(config_path) as f:
        parameters = json.load(f)

    retrieve_dicoms_using_table(table, parameters, out_directory, True, True, False)

    # Assert the first six files of the list are correct
    output_files = glob(os.path.join(out_directory, "sub-*/ses-*/*/*"))
    known_files_dir = os.path.join(
        test_dir, "tmp", "test_set", "sub-PACSMAN1", "ses-20231016"
    )
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

    # Check if the log CSV file was created
    log_csv_path = os.path.join(out_directory, "logs", "pacsifier_log.csv")
    assert os.path.exists(log_csv_path), f"CSV log file {log_csv_path} was not created."


def test_upload_dicoms(test_dir):
    dicomseries_karnak_tags_dir = os.path.join(
        test_dir, "tmp", "test_data", "dicomseries_tagged_all"
    )
    config_path = os.path.join(test_dir, "config", "config_upload.json")
    with open(config_path) as f:
        parameters = json.load(f)
    upload_dicoms(dicomseries_karnak_tags_dir, parameters)


def test_count_dicoms_using_table(monkeypatch, tmp_path, capsys):
    table = _build_minimal_table()
    parameters = _build_minimal_parameters()
    output_dir = tmp_path / "out"

    monkeypatch.setattr(pacsifier_cli, "echo", lambda **_: True)
    monkeypatch.setattr(pacsifier_cli, "find", lambda *_, **__: "FIND")

    def _fake_write_file(_results, file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        Path(file).write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "write_file", _fake_write_file)
    monkeypatch.setattr(
        pacsifier_cli,
        "parse_findscu_count_dump_file",
        lambda *_: [
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.3",
                "NumberOfStudyRelatedSeries": "2",
                "NumberOfStudyRelatedInstances": "42",
            },
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.4",
                "NumberOfStudyRelatedSeries": "3",
                "NumberOfStudyRelatedInstances": "84",
            },
        ],
    )

    count_dicoms_using_table(
        table=table,
        parameters=parameters,
        output_dir=str(output_dir),
        verbose=False,
    )

    out = capsys.readouterr().out
    assert "Count summary:" in out
    assert "PatientID=PACSMAN1: studies=2, series=5, instances=126" in out


def _build_minimal_table():
    """Create a minimal query table for resume tests."""
    record = {field: "" for field in ALLOWED_FILTERS}
    record.update(
        {
            "PatientID": "PACSMAN1",
            "StudyDate": "20231016",
            "SeriesDescription": "TestSeries",
            "SeriesNumber": "1",
            "StudyInstanceUID": "1.2.826.0.1.3680043.2.1125.1",
            "SeriesInstanceUID": "1.2.826.0.1.3680043.2.1125.1.1",
        }
    )
    return DataFrame([record], columns=ALLOWED_FILTERS)


def _build_minimal_parameters():
    return {
        "server_address": "localhost",
        "port": 4444,
        "server_AET": "SCU_STORE",
        "AET": "PACSIFIER_SCU",
        "move_port": 11112,
        "move_AET": "PACSIFIER_CLIENT",
        "batch_wait_time": 0,
        "batch_size": 1,
    }


def _mock_series_entry():
    return [
        {
            "PatientID": "PACSMAN1",
            "StudyDate": "20231016",
            "StudyTime": "",
            "SeriesDescription": "TestSeries",
            "SeriesNumber": "1",
            "StudyInstanceUID": "1.2.826.0.1.3680043.2.1125.1",
            "SeriesInstanceUID": "1.2.826.0.1.3680043.2.1125.1.1",
        }
    ]


class _DummyProgressBar:
    def __call__(self, iterable):
        return iterable


def _setup_retrieve_mocks(monkeypatch, series_list, get_stub):
    monkeypatch.setattr(pacsifier_cli, "echo", lambda **_: True)
    monkeypatch.setattr(pacsifier_cli, "find", lambda *_, **__: "FIND")

    def _fake_write_file(_results, file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        Path(file).write_text("", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "write_file", _fake_write_file)
    monkeypatch.setattr(
        pacsifier_cli, "parse_findscu_dump_file", lambda *_: series_list
    )
    monkeypatch.setattr(pacsifier_cli, "ProgressBar", _DummyProgressBar)
    monkeypatch.setattr(pacsifier_cli, "get", get_stub)
    monkeypatch.setattr(pacsifier_cli, "move_remote", lambda *_, **__: None)


def _expected_series_dir(output_dir: Path) -> Path:
    return (
        output_dir
        / "sub-PACSMAN1"
        / "ses-20231016"
        / "00001-TestSeries"
    )


def test_resume_skips_existing_series(monkeypatch, tmp_path):
    table = _build_minimal_table()
    parameters = _build_minimal_parameters()
    output_dir = tmp_path / "out"
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    series_dir = _expected_series_dir(output_dir)
    series_dir.mkdir(parents=True, exist_ok=True)
    (series_dir / "image_000.dcm").write_text("dummy", encoding="utf-8")

    calls = []

    def _fake_get(*args, **kwargs):
        calls.append((args, kwargs))

    _setup_retrieve_mocks(monkeypatch, _mock_series_entry(), _fake_get)

    retrieve_dicoms_using_table(
        table,
        parameters,
        str(output_dir),
        save=True,
        info=False,
        move=False,
        resume=True,
    )

    assert calls == []


def test_resume_downloads_when_directory_empty(monkeypatch, tmp_path):
    table = _build_minimal_table()
    parameters = _build_minimal_parameters()
    output_dir = tmp_path / "out"
    (output_dir / "logs").mkdir(parents=True, exist_ok=True)

    calls = []

    def _fake_get(*args, **kwargs):
        calls.append((args, kwargs))

    _setup_retrieve_mocks(monkeypatch, _mock_series_entry(), _fake_get)

    retrieve_dicoms_using_table(
        table,
        parameters,
        str(output_dir),
        save=True,
        info=False,
        move=False,
        resume=True,
    )

    assert len(calls) == 1


def test_check_output_info():
    pass

    # pacsifier.main([
    #     "--info", "--queryfile test.csv", "--out_directory ./tests/test_set",
    #     "--config ./files/config.json"
    # ])
    # subjects = glob("./test_set/*")
    # sessions = glob("./test_set/sub-*/ses-*")
    # csv_files = glob("./test_set/sub-*/ses-*/*.csv")

    # assert subjects == ['./test_set/sub-XXX']
    # assert sessions == ['./test_set/sub-XXX/ses-YYY', './test_set/sub-XXX/ses-ZZZ']
    # assert csv_files == ['./test_set/sub-XXX/ses-YYY/foo.csv', ... ]
