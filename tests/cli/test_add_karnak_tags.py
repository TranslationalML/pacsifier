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

"""Test for the functions of the `pacsifier.cli.add_karnak_tags` script."""

import os
from glob import glob
import shutil
import sys
import pydicom


from pacsifier.cli.add_karnak_tags import (
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
        patient_code="PACSIFIER2",
        patient_shift="10",
        album_name="PACSIFIERCohort",
    )
    dataset = pydicom.read_file(file_to_tag)

    # Check that the tags have been added
    assert dataset[0x000B, 0x1001].value == "PACSIFIER2"
    assert dataset[0x000B, 0x1002].value == "PACSIFIERCohort"
    assert dataset[0x000B, 0x1003].value == "10"


def test_tag_all_dicoms_within_root_folder(test_dir):
    in_folder = os.path.join(test_dir, "test_data", "dicomseries")
    folder_to_tag = os.path.join(test_dir, "tmp", "test_data", "dicomseries_tagged_all")
    if not os.path.exists(folder_to_tag):
        os.makedirs(folder_to_tag, exist_ok=True)
    patient_ids = ["PACSIFIER1", "PACSIFIER2", "PACSIFIER3"]
    session_folders = ["ses-20231006", "ses-20231016", "ses-20231026"]
    series_folders = ["00000_series", "00001_series"]
    files = ["slice0.dcm", "slice1.dcm", "slice2.dcm"]

    for patient_id in patient_ids:
        for session_folder in session_folders:
            for series_folder in series_folders:
                series_path = os.path.join(
                    folder_to_tag, f"sub-{patient_id}", session_folder, series_folder
                )
                if os.path.exists(os.path.join(series_path)):
                    shutil.rmtree(os.path.join(series_path))
                os.makedirs(series_path)
                for file in files:
                    shutil.copy(
                        os.path.join(in_folder, file), os.path.join(series_path, file)
                    )
                    # Update PatientID Tag
                    dataset = pydicom.read_file(os.path.join(series_path, file))
                    dataset.PatientID = patient_id
                    # Update StudyDate Tag with correct VR DA format (YYYYMMDD)
                    dataset.StudyDate = str(session_folder.split("-")[1])
                    # TODO: Update PatientID / StudyInstanceUID / SeriesInstanceUID Tag
                    # to be able to load the different series in Weasis.
                    # For now, we have to "remove the patient" from Weasis to load the different series.
                    dataset.save_as(os.path.join(series_path, file))

    patient_codes = ["PACSIFIER1coded", "PACSIFIER2coded", "PACSIFIER3coded"]
    day_shifts = ["10", "20", "30"]

    tag_all_dicoms_within_root_folder(
        data_path=folder_to_tag,
        new_ids={
            f"sub-{real_id}": coded_id
            for real_id, coded_id in zip(patient_ids, patient_codes)
        },
        day_shift={
            f"sub-{real_id}": day_shift
            for real_id, day_shift in zip(patient_ids, day_shifts)
        },
        album_name="PACSIFIERCohort",
    )

    # Check that the new private tags have been added
    for patient_id, patient_code, day_shift in zip(
        patient_ids, patient_codes, day_shifts
    ):
        for file in glob(
            os.path.join(folder_to_tag, f"sub-{patient_id}", "*", "*", "*")
        ):
            dataset = pydicom.read_file(file)
            assert dataset[0x000B, 0x1001].value == patient_code
            assert dataset[0x000B, 0x1002].value == "PACSIFIERCohort"
            assert dataset[0x000B, 0x1003].value == day_shift
