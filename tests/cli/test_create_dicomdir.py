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

"""Tests for the function of the `pacsifier.cli.create_dicomdir` script."""

import os
from glob import glob
import pydicom

from pacsifier.cli.create_dicomdir import (
    generate_new_folder_name,
    add_or_retrieve_name,
    move_and_rename_files,
    create_dicomdir,
)


def test_generate_new_folder_name():
    names = ["12345678", "abcdefgh"]
    name = generate_new_folder_name(names=names)
    assert name not in names
    assert len(name) <= 8
    assert len(name) >= 4
    assert name.isalnum()


def test_add_or_retrieve_name():
    old_2_new = {}
    names = []
    current_folder = "12345678"
    folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
    assert folder_name not in names
    assert len(folder_name) <= 8
    assert len(folder_name) >= 4
    assert folder_name.isalnum()
    assert folder_name == old_2_new[current_folder]
    names.append(folder_name)

    current_folder = "abcdefgh"
    folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
    assert folder_name not in names
    assert len(folder_name) <= 8
    assert len(folder_name) >= 4
    assert folder_name.isalnum()
    assert folder_name == old_2_new[current_folder]
    names.append(folder_name)


def test_move_and_rename_files(test_dir):
    dicom_path = os.path.join(test_dir, "tmp", "test_data", "dicomseries_structured")
    # Add StudyID, StudyTime and SeriesNumber to the DICOM files
    # SeriesNumber is taken from the dicom name (slice0.dcm, slice1.dcm, etc.) incremented by 1
    # Such that the first file has SeriesNumber 1
    # This is required for the DICOMDIR creation. Otherwise dcmmkdir --recurse ./ will fail.
    # StudyID and StudyTime are set arbitrarily.
    series_path = os.path.join(dicom_path, "sub-PACSIFIER1", "ses-20232016", "00000-No_series_description")
    for i, file in enumerate(sorted(glob(os.path.join(series_path, "*.dcm")))):
        dataset = pydicom.read_file(file)
        dataset.StudyID = "12345678"
        dataset.StudyTime = "101601.934000"
        dataset.SeriesNumber = str(i)
        dataset.save_as(file)

    output_path = os.path.join(test_dir, "tmp", "test_data", "dicomseries_move_and_rename")
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    move_and_rename_files(dicom_path, output_path)
    # Assess that the number of files in the output folder is the same
    # as in the input folder
    assert len(
        glob(os.path.join(output_path, "*", "*", "*", "*"))
    ) == len(
        glob(os.path.join(dicom_path, "*", "*", "*", "*"))
    )


def test_create_dicomdir(test_dir):
    # Employed the same output path generated by test_move_and_rename_files
    output_path = os.path.join(test_dir, "tmp", "test_data", "dicomseries_move_and_rename")
    create_dicomdir(output_path)
