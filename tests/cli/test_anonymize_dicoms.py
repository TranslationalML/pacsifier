"""Tests for the functions of the anonymize_dicoms script.""" ""

import random
import pytest

from pacsman.cli.anonymize_dicoms import fuzz_date


def test_fuzz_date():
    fuzzed, offset_days = fuzz_date("20180911", fuzz_parameter=2)
    assert fuzzed in ["20180910", "20180909", "20180911", "20180912", "20180913"]
    assert abs(offset_days) <= 2
    with pytest.raises(ValueError):
        fuzz_date("20180911", fuzz_parameter=random.randint(-10000, 0))


# def test_anonymize():
#     in_file = "/tests/test_data/rubo_sample_file_0003.DCM"
#     out_file = "/tests/test_data/rubo_sample_file_0003_anon.DCM"
#     anonymize_dicom_file(
#         in_file,
#         out_file,
#         PatientID="00042",
#         new_StudyInstanceUID="0000001.01",
#         new_SeriesInstanceUID="000012.01",
#         new_SOPInstanceUID="000000010.101",
#         fuzz_birthdate=True,
#         fuzz_acqdates=True,
#         fuzz_days_shift=10,
#         delete_identifiable_files=True,
#         remove_private_tags=False,
#     )
#     dataset = pydicom.read_file(out_file)
#     attributes = dataset.dir("")

#     assert dataset.PatientID == "00042"
#     assert dataset.PatientName == "00042^sub"
#     assert dataset.InstitutionAddress == "Address"
#     assert (
#         dataset.PatientBirthDate == "19580729"
#     )  # original date PatientBirthDate 19580719 -> check + 10 days shift
#     assert dataset.StudyDate == "19930404"  # original StudyDate 19930325
#     if "ReferringPhysicianTelephoneNumbers" in attributes:
#         assert dataset.ReferringPhysicianTelephoneNumbers == ""
#     if "PatientTelephoneNumbers" in attributes:
#         assert dataset.PatientTelephoneNumbers == ""
#     if "PersonTelephoneNumbers" in attributes:
#         assert dataset.PersonTelephoneNumbers == ""
#     if "orderCallbackPhoneNumber" in attributes:
#         assert dataset.OrderCallbackPhoneNumber == ""
#     if "InstitutionName" in attributes:
#         assert dataset.InstitutionName == ""

#     if "ReferringPhysiciansAddress" in attributes:
#         assert dataset.ReferringPhysiciansAddress == ""

#     if "ReferringPhysicianIDSequence" in attributes:
#         assert dataset.ReferringPhysicianIDSequence == ""

#     if "InstitutionalDepartmentName" in attributes:
#         assert dataset.InstitutionalDepartmentName == ""

#     if "PhysicianOfRecord" in attributes:
#         assert dataset.PhysicianOfRecord == ""

#     if "PerformingPhysicianName" in attributes:
#         assert dataset.PerformingPhysicianName == ""

#     if "ReferringPhysiciansAddress" in attributes:
#         assert dataset.ReferringPhysiciansAddress == ""

#     if "ReferringPhysiciansTelephoneNumber" in attributes:
#         assert dataset.ReferringPhysiciansTelephoneNumber == ""

#     if "PerformingPhysicianIDSequence" in attributes:
#         assert dataset.PerformingPhysicianIDSequence == ""

#     if "NameOfPhysicianReadingStudy" in attributes:
#         assert dataset.NameOfPhysicianReadingStudy == ""

#     if "PhysicianReadingStudyIDSequence" in attributes:
#         assert dataset.PhysicianReadingStudyIDSequence == ""

#     if "OperatorsName" in attributes:
#         assert dataset.OperatorsName == ""

#     if "IssuerOfPatientID" in attributes:
#         assert dataset.IssuerOfPatientID == ""

#     if "PatientsBirthTime" in attributes:
#         assert dataset.PatientsBirthTime == ""

#     if "OtherPatientIDs" in attributes:
#         assert dataset.OtherPatientIDs == ""

#     if "OtherPatientNames" in attributes:
#         assert dataset.OtherPatientNames == ""

#     if "PatientBirthName" in attributes:
#         assert dataset.PatientBirthName == ""

#     if "PersonAddress" in attributes:
#         assert dataset.PersonAddress == ""

#     if "PatientMotherBirthName" in attributes:
#         assert dataset.PatientMotherBirthName == ""

#     if "CountryOfResidence" in attributes:
#         assert dataset.CountryOfResidence == ""

#     if "RegionOfResidence" in attributes:
#         assert dataset.RegionOfResidence == ""

#     if "CurrentPatientLocation" in attributes:
#         assert dataset.CurrentPatientLocation == ""

#     if "PatientInstitutionResidence" in attributes:
#         assert dataset.PatientsInstitutionResidence == ""

#     if "PersonName" in attributes:
#         assert dataset.PersonName == ""

#     dataset.PatientAge = "091"
#     dataset.save_as("/tests/test_data/temp_output_sample_image.DCM")

#     anonymize_dicom_file(
#         "/tests/test_data/temp_output_sample_image.DCM",
#         "/tests/test_data/temp_output_sample_image.DCM",
#         PatientID="00042",
#         new_StudyInstanceUID="0000001.01",
#         new_SeriesInstanceUID="000012.01",
#         new_SOPInstanceUID="000000010.101",
#         fuzz_birthdate=True,
#         fuzz_acqdates=False,
#         fuzz_days_shift=5,
#         delete_identifiable_files=True,
#         remove_private_tags=False,
#     )

#     dataset = pydicom.read_file("/tests/test_data/temp_output_sample_image.DCM")
#     assert dataset.PatientAge == "90+Y"


# def test_anonymize_all_dicoms_within_folder():
#     dict_ = anonymize_all_dicoms_within_root_folder(
#         output_folder=".",
#         datapath=".",
#         pattern_dicom_files="output_sample_image",
#         rename_patient_directories=False,
#     )
#     # print(dict_)
#     # assert dict_ == {'000003': '__pycache__', '000002': 'test_set', '000000': '.pytest_cache', '000001': '.hypothesis'}
