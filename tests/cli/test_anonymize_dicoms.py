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

"""Tests for the functions of the `pacsman.cli.anonymize_dicoms` script.""" ""

import os
import random
import shutil
import sys
import pytest

import pydicom

from pacsman.cli.anonymize_dicoms import (
    fuzz_date,
    anonymize_dicom_file,
    anonymize_all_dicoms_within_root_folder,
)


def test_fuzz_date():
    fuzzed, offset_days = fuzz_date("20180911", fuzz_parameter=2)
    assert fuzzed in ["20180910", "20180909", "20180911", "20180912", "20180913"]
    assert abs(offset_days) <= 2
    with pytest.raises(ValueError):
        fuzz_date("20180911", fuzz_parameter=random.randint(-10000, 0))


def test_anonymize(test_dir):
    in_file = os.path.join(test_dir, "test_data", "dicomseries", "slice0.dcm")
    out_dir = os.path.join(test_dir, "tmp", "test_data", "dicomseries_anon")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "slice0.dcm")

    # Get StudyInstanceUID, SeriesInstanceUID and SOPInstanceUID from the original file
    # to increment them by 1 in the anonymized file
    dataset = pydicom.read_file(in_file)
    StudyInstanceUID = dataset.StudyInstanceUID
    SeriesInstanceUID = dataset.SeriesInstanceUID
    SOPInstanceUID = dataset.SOPInstanceUID
    new_StudyInstanceUID = StudyInstanceUID.split(".")
    new_StudyInstanceUID[-1] = str(int(new_StudyInstanceUID[-1]) + 1)
    new_StudyInstanceUID = ".".join(new_StudyInstanceUID)
    new_SeriesInstanceUID = SeriesInstanceUID.split(".")
    new_SeriesInstanceUID[-1] = str(int(new_SeriesInstanceUID[-1]) + 1)
    new_SeriesInstanceUID = ".".join(new_SeriesInstanceUID)
    new_SOPInstanceUID = SOPInstanceUID.split(".")
    new_SOPInstanceUID[-1] = str(int(new_SOPInstanceUID[-1]) + 1)
    new_SOPInstanceUID = ".".join(new_SOPInstanceUID)

    # Test if the anonymization works
    anonymize_dicom_file(
        in_file,
        out_file,
        PatientID="PACSMAN2",
        new_StudyInstanceUID=new_StudyInstanceUID,
        new_SeriesInstanceUID=new_SeriesInstanceUID,
        new_SOPInstanceUID=new_SOPInstanceUID,
        fuzz_birthdate=True,
        fuzz_acqdates=True,
        fuzz_days_shift=10,
        delete_identifiable_files=True,
        remove_private_tags=False,
    )

    dataset = pydicom.read_file(out_file)
    attributes = dataset.dir("")

    assert dataset.PatientID == "PACSMAN2"
    assert dataset.PatientName == "PACSMAN2^sub"
    if "InstitutionAddress" in attributes:
        assert dataset.InstitutionAddress == "Address"
    if "PatientBirthDate" in attributes:
        assert (
            dataset.PatientBirthDate == "20231026"
        )  # original date PatientBirthDate 20231016 -> check + 10 days shift
    assert (
        dataset.StudyDate == "20231026"
    )  # original StudyDate 20231016 -> check + 10 days shift
    if "ReferringPhysicianTelephoneNumbers" in attributes:
        assert dataset.ReferringPhysicianTelephoneNumbers == ""
    if "PatientTelephoneNumbers" in attributes:
        assert dataset.PatientTelephoneNumbers == ""
    if "PersonTelephoneNumbers" in attributes:
        assert dataset.PersonTelephoneNumbers == ""
    if "orderCallbackPhoneNumber" in attributes:
        assert dataset.OrderCallbackPhoneNumber == ""
    if "InstitutionName" in attributes:
        assert dataset.InstitutionName == ""
    if "ReferringPhysiciansAddress" in attributes:
        assert dataset.ReferringPhysiciansAddress == ""
    if "ReferringPhysicianIDSequence" in attributes:
        assert dataset.ReferringPhysicianIDSequence == ""
    if "InstitutionalDepartmentName" in attributes:
        assert dataset.InstitutionalDepartmentName == ""
    if "PhysicianOfRecord" in attributes:
        assert dataset.PhysicianOfRecord == ""
    if "PerformingPhysicianName" in attributes:
        assert dataset.PerformingPhysicianName == ""
    if "ReferringPhysiciansAddress" in attributes:
        assert dataset.ReferringPhysiciansAddress == ""
    if "ReferringPhysiciansTelephoneNumber" in attributes:
        assert dataset.ReferringPhysiciansTelephoneNumber == ""
    if "PerformingPhysicianIDSequence" in attributes:
        assert dataset.PerformingPhysicianIDSequence == ""
    if "NameOfPhysicianReadingStudy" in attributes:
        assert dataset.NameOfPhysicianReadingStudy == ""
    if "PhysicianReadingStudyIDSequence" in attributes:
        assert dataset.PhysicianReadingStudyIDSequence == ""
    if "OperatorsName" in attributes:
        assert dataset.OperatorsName == ""
    if "IssuerOfPatientID" in attributes:
        assert dataset.IssuerOfPatientID == ""
    if "PatientsBirthTime" in attributes:
        assert dataset.PatientsBirthTime == ""
    if "OtherPatientIDs" in attributes:
        assert dataset.OtherPatientIDs == ""
    if "OtherPatientNames" in attributes:
        assert dataset.OtherPatientNames == ""
    if "PatientBirthName" in attributes:
        assert dataset.PatientBirthName == ""
    if "PersonAddress" in attributes:
        assert dataset.PersonAddress == ""
    if "PatientMotherBirthName" in attributes:
        assert dataset.PatientMotherBirthName == ""
    if "CountryOfResidence" in attributes:
        assert dataset.CountryOfResidence == ""
    if "RegionOfResidence" in attributes:
        assert dataset.RegionOfResidence == ""
    if "CurrentPatientLocation" in attributes:
        assert dataset.CurrentPatientLocation == ""
    if "PatientInstitutionResidence" in attributes:
        assert dataset.PatientsInstitutionResidence == ""
    if "PersonName" in attributes:
        assert dataset.PersonName == ""

    # Test if age is properly handled
    in_file_new_age = os.path.join(
        test_dir, "tmp", "test_data", "dicomseries_anon", "slice0_newage.dcm"
    )
    out_file_new_age = os.path.join(
        test_dir, "tmp", "test_data", "dicomseries_anon", "slice0_newage_anon.dcm"
    )

    if os.path.exists(in_file_new_age):
        os.remove(in_file_new_age)
    if os.path.exists(out_file_new_age):
        os.remove(out_file_new_age)

    dataset.PatientAge = "091Y"
    dataset.save_as(in_file_new_age)

    anonymize_dicom_file(
        in_file_new_age,
        out_file_new_age,
        PatientID="PACSMAN2",
        new_StudyInstanceUID=new_StudyInstanceUID,
        new_SeriesInstanceUID=new_SeriesInstanceUID,
        new_SOPInstanceUID=new_SOPInstanceUID,
        fuzz_birthdate=True,
        fuzz_acqdates=False,
        fuzz_days_shift=5,
        delete_identifiable_files=True,
        remove_private_tags=False,
    )

    dataset = pydicom.read_file(out_file_new_age)
    # WARNING: 90+Y is not a valid DICOM age value
    # This might have to be fixed in anonymize_dicom_file()
    # in the future.
    # For now, this raises a Warning in the test.
    assert dataset.PatientAge == "90+Y"


def test_anonymize_all_dicoms_within_folder(test_dir):
    # Create a folder with a few files following the expected structure
    dicom_dir = os.path.join(test_dir, "test_data", "dicomseries")
    pacsman_dir = os.path.join(test_dir, "tmp", "test_data", "dicomseries_structured")
    structured_series_dir = os.path.join(
        pacsman_dir, "sub-PACSMAN1", "ses-20232016", "00000-No_series_description"
    )
    anonymization_dir = os.path.join(
        test_dir, "tmp", "test_data", "dicomseries_structured_anon"
    )

    for dir in [structured_series_dir, anonymization_dir]:
        if os.path.exists(dir):
            shutil.rmtree(dir, ignore_errors=True)
        os.makedirs(dir, exist_ok=True)

    for dir, _, files in os.walk(dicom_dir):
        for f in files:
            if f.endswith(".dcm"):
                shutil.copyfile(
                    os.path.join(dir, f), os.path.join(structured_series_dir, f)
                )

    dict_ = anonymize_all_dicoms_within_root_folder(
        output_folder=anonymization_dir,
        datapath=pacsman_dir,
        pattern_dicom_files=os.path.join("ses-*", "*", "*.dcm"),
        rename_patient_directories=False,
    )
    assert dict_ == {"000001": "PACSMAN1"}
