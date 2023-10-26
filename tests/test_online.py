"""
Test functions requiring connectivity to a DICOM server
"""
import sys

from pacsman.core.execute_commands import *
import pacsman.cli.pacsman as pacsman
from pacsman.cli.pacsman import *
from pacsman.core.sanity_checks import *
import pytest
from pacsman.cli.anonymize_dicoms import *
from pacsman.cli.convert import *
import os
from functools import reduce
from hypothesis import given, example
from pacsman.cli.create_dicomdir import *
import pacsman.cli.move_dumps as move_dumps
from hypothesis.strategies import text, integers

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! for coverage execute : py.test --cov=../../ testing.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ../../ points to the project folder !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# TODO update for DICOMserverUK
def test_retrieve():
    # Retrieve DICOM series
    table = read_csv("/tests/test_data/query/query_dicom.csv", dtype=str).fillna("")
    config_path = os.path.join("/tests/config/config.json")

    with open(config_path) as f:
        parameters = json.load(f)

    out_directory = os.path.join("/tests", "tmp", "test_set")
    # retrieve_dicoms_using_table(table, parameters, out_directory, False, False)

    # assert glob("./test_set/sub-*/ses-*/*/*") == []
    # retrieve_dicoms_using_table(table, parameters, out_directory, False, True)

    # assert glob("./test_set/sub-*/ses-*/*/*") == []
    retrieve_dicoms_using_table(table, parameters, out_directory, True, True, False)

    output_files = glob("/tests/tmp/test_set/sub-*/ses-*/*/*")

    known_files = [
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10078350936423615213975808998561561261",
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10079063413960953608145500849488605317",
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10254832511701611336169372822417032099",
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10297714540640569882794200001611356979",
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10299592168011030062855381217267705761",
        "/tests/tmp/test_set/sub-PACSMAN1/ses-20231016/00000-No_series_description/MR.1.2.826.0.1.3680043.8.498.10773050947549757012436832094131147157",
    ]

    assert sorted(output_files)[:6] == sorted(known_files)[:6]


# TODO update this to use DICOMserverUK
def test_check_output_info():
    pass

    # pacsman.main(["--info", "--queryfile test.csv", "--out_directory ./tests/test_set",  "--config ./files/config.json"])
    # subjects = glob("./test_set/*")
    # sessions = glob("./test_set/sub-*/ses-*")
    # csv_files = glob("./test_set/sub-*/ses-*/*.csv")

    # assert subjects == ['./test_set/sub-XXX']
    # assert sessions == ['./test_set/sub-XXX/ses-YYY', './test_set/sub-XXX/ses-ZZZ']
    # assert csv_files == ['./test_set/sub-XXX/ses-YYY/foo.csv', ... ]
