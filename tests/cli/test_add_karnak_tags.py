"""Test for the functions of the add_karnak_tags script."""

import os
from glob import glob
import shutil
import sys
import pytest
import pydicom


from pacsman.cli.add_karnak_tags import (
    tag_dicom_file,
    tag_all_dicoms_within_root_folder,
)


def test_tag_dicom_file(test_dir):
    in_file = os.path.join(test_dir, "test_data", "dicomseries", "slice0.dcm")
    out_dir = os.path.join(test_dir, "tmp", "test_data", "dicomseries_tagged")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    file_to_tag = os.path.join(out_dir, "slice0.dcm")
    if os.path.exists(file_to_tag):
        os.remove(file_to_tag)
    shutil.copy(in_file, file_to_tag)

    tag_dicom_file(
        file_to_tag,
        patient_code="PACSMAN2",
        patient_shift="10",
        album_name="PACSMANCohort",
    )
    dataset = pydicom.read_file(file_to_tag)
    print(dataset, file=sys.stderr)

    # Check that the tags have been added
    assert dataset[0x000B, 0x1001].value == "PACSMAN2"
    assert dataset[0x000B, 0x1002].value == "PACSMANCohort"
    assert dataset[0x000B, 0x1003].value == "10"

