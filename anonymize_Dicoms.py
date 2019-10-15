import warnings
import pydicom
from datetime import datetime, timedelta
from glob import glob
import sys
import os
from tqdm import tqdm
import random
import json
from typing import Dict
import argparse
import hashlib


def fuzz_date(date: str, fuzz_parameter: int = 30) -> str:
    """
    Fuzzes date in a range of fuzz_parameter days prior to fuzz_parameter days after.
    Args :
        date: date in YYYYMMDD format.
        fuzz_parameter: the number of days by which the date will be fuzzed.
    Returns :
        string : new fuzzed date.
    """
    if fuzz_parameter <= 0:
        raise ValueError("Fuzz parameter must be strictly positive!")

    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])

    # Generating random fuzz parameter.
    fuzz = random.randint(-fuzz_parameter, fuzz_parameter)

    # Processing new date.
    date_time = datetime(day=day, month=month, year=year)  # type : datetime
    str_date = (date_time + timedelta(days=fuzz)).strftime("%Y%m%d")  # type : str

    del date_time
    return str_date


def anonymize_dicom_file(
        filename: str,
        output_filename: str,
        PatientID: str,
        PatientID_numstr: str,
        fuzzed_birthdate: str,
        delete_identifiable_files: bool) -> None:
    """
    Anonymizes the dicom image located at filename by affecting  patient id, patient name and date.
    If identifiable data is present, deletes the file

    Args :
        filename: path to dicom image.
        output_filename: output path of anonymized image.
        PatientID: the new patientID after anonymization.
        PatientID_numstr: a string of 0-9 digits corresponding to the patient ID (e.g. hashed) to be used in DICOM fields that need digits rather
            than alphanums. Example: '9292919239516130'
        fuzzed_birthdate: a fuzzed birthdate for this patient
        delete_identifiable_files: Should we delete DICOM Series which have identifiable information in the image data itself?
            This is the case for example for screen saves for dose reports coming from the GE Revolution CT machine, which have the patient name embedded.
            Also the case for screen saves for dose reports from Toshiba/Canon Aquilion Prime, although these don't have SCREEN SAVE label in ImageType tyg

    TODO:
        - Implement proper exception handling
        - Check if resulting anonimized StudyInstanceUID conforms to the proper VR (should be < 64 chars?)
    """

    # Load the current dicom file to 'anonymize'
    try:
        dataset = pydicom.read_file(filename)
    except pydicom.errors.InvalidDicomError:
        print("Error at file at path :  " + filename)
        pass

    ninety_plus = False
    delete_this_file = False
    attributes = dataset.dir("")

    if delete_identifiable_files:
        if "ImageType" in attributes:
            if 'SCREEN SAVE' in dataset.data_element('ImageType').value:
                delete_this_file = True
            if 'SECONDARY' in dataset.data_element('ImageType').value and 'CT' in dataset.data_element('Modality').value:
                delete_this_file = True

    if delete_this_file:
        os.remove(filename)
    else:
        if "PatientID" in attributes:
            old_id = dataset.PatientID
            dataset.PatientID = PatientID

        # Reuse the 16-digits numeric string patient ID here, which also correspond to a SH VR
        if "AccessionNumber" in attributes:
            # dataset.AccessionNumber = ""
            dataset.AccessionNumber = PatientID_numstr

        if "PatientName" in attributes:
            # make it a valid PN VR
            dataset.PatientName = PatientID + "^sub"

        if "InstitutionAddress" in attributes:
            dataset.InstitutionAddress = "Address"

        elements_to_blank = ["CurrentPatientLocation", "CountryOfResidence", "InstitutionalDepartmentName",
                             "InstitutionName", "IssuerOfPatientID", "NameOfPhysicianReadingStudy",
                             "OperatorsName", "OrderCallbackPhoneNumber", "OtherPatientNames", "OtherPatientIDs",
                             "PatientAddress", "PatientBirthName", "PatientsBirthTime",
                             "PatientInstitutionResidence", "PatientMotherBirthName", "PatientTelephoneNumbers",
                             "PersonAddress", "PersonName",
                             "PersonTelephoneNumbers", "PerformingPhysicianIDSequence", "PerformingPhysicianName",
                             "PhysiciansReadingStudyIdentificationSequence", "PhysicianOfRecord",
                             "RegionOfResidence", "ReferringPhysiciansAddress", "ReferringPhysicianIDSequence",
                             "ReferringPhysiciansName", "ReferringPhysicianTelephoneNumbers"]
        # note: OtherPatientIDs is a retired attribute
        for el in elements_to_blank:
            if el in attributes:
                dataset.data_element(el).value = ""

        # now take care of age
        try:
            age = dataset.PatientAge

            # If age attribute is an empty string, skip this step all together
            if age != '':
                if int(age[:3]) > 89:
                    ninety_plus = True
                    dataset.PatientAge = "90+Y"
                    dataset.PatientBirthDate = "19010101"
        except AttributeError:
            pass

        # One of the components of the StudyInstanceUID sometimes contains the original patientID (e.g. on GE Revolution CT machines).
        # Therefore, the original patientID should be replaced by the new anonymous one.
        # But DICOM standard part 5 chapter 9.1 'UID encoding rules' says 'Each component of a UID is a number and
        # shall consist of one or more digits', and 'Each component numeric value shall be encoded using the characters 0-9'
        # So we use a numeric equivalent instead of the new_id which has no restrictions

        if "StudyInstanceUID" in attributes:
            studyUID = dataset.StudyInstanceUID
            dataset.StudyInstanceUID = studyUID.replace(old_id, PatientID_numstr)

        # we also have to fix the potentially referrring tags
        # RequestAttributesSequence 0040,0275 is type 3, so optional, we should be able to delete it
        # ReferencedStudySequence 0008,1110 is type 3 in GENERAL STUDY MODULE ATTRIBUTES (type 2 in other modules), so we could also delete it
        # - RequestAttributesSequence > ReferencedStudySequence > ReferencedSOPInstanceUID
        # or
        # - RequestAttributesSequence >  StudyInstanceUID
        # or
        # - RequestAttributesSequence > Accession Number
        # Also
        # - ReferencedStudySequence > ReferencedSOPInstanceUID

        if "RequestAttributesSequence" in attributes:
            del dataset.RequestAttributesSequence

        if "ReferencedStudySequence" in attributes:
            del dataset.ReferencedStudySequence
        # 	ReferencedStudySequence = dataset.ReferencedStudySequence
        # 	dataset.ReferencedStudySequence = ReferencedStudySequence.replace(old_id, PatientID_numstr)

        # if "ReferencedSOPInstanceUID" in attributes : # 0008,1155 - only seems to exist in RequestAttributesSequence
        #	del dataset.ReferencedSOPInstanceUID
        # 	ReferencedSOPInstanceUID = dataset.ReferencedSOPInstanceUID
        # 	dataset.ReferencedSOPInstanceUID = ReferencedSOPInstanceUID.replace(old_id, PatientID_numstr)

        if 'PatientBirthDate' in dataset:
            # Assign a new fuzzed birth date.
            dataset.data_element('PatientBirthDate').value = fuzzed_birthdate
            if not ninety_plus:
                # Change the age of the patient according to the new fuzzed birth date.
                new_age = str(int((datetime.strptime(dataset.StudyDate, "%Y%m%d") - datetime.strptime(fuzzed_birthdate,
                                                                                                      "%Y%m%d")).days / 365))
                try:
                    dataset.PatientAge = str(new_age).zfill(3) + "Y"
                except AttributeError:
                    pass

        # write the 'anonymized' DICOM out under the new filename
        dataset.save_as(output_filename)


def anonymize_all_dicoms_within_root_folder(
        output_folder: str = ".",
        datapath: str = os.path.join(".", "data"),
        pattern_dicom_files: str = os.path.join("ses-*", "*", "*"),
        new_ids: str = None,
        rename_patient_directories: bool = True,
        delete_identifiable_files: bool = True) -> Dict[str, str]:
    """
    Anonymizes all dicom images located at the datapath in the structure specified by pattern_dicom_files parameter.
    Args :
        output_folder: path where anonymized images will be located.
        datapath: The path to the dicom images.
        pattern_dicom_files: the (generic) path to the dicom images starting from the patient folder. In a PACSMAN dump, this would reflect e.g.
            ses-20170115/0002-MPRAGE/*.dcm
        new_ids : The anonymous ids to be set after anonymizing the original ids.
        rename_patient_directories : Should we rename_patient_directories patient directories using the anonymized ids?
        delete_identifiable_files: Should we delete DICOM Series which have identifiable information in the image data itself?
            This is the case for example for screen saves coming from the GE Revolution CT machine, which have the patient name embedded.
    Returns :
        dict : Dictionary keeping track of the new patientIDs and old patientIDs mappings.
    """

    # TODO: fix required vs optional arguments

    # Listing patient files.

    patients_folders = next(os.walk(datapath))[1]
    if new_ids is None:
        new_ids = {patients_folders[i]: str(i).zfill(6) for i in range(len(patients_folders))}

    # Keep a mapping from old to new ids in a dictionary.
    old2new_idx = {patients_folders[i]: new_ids[patients_folders[i]] for i in range(len(patients_folders))}
    old2set_idx = {}
    # Loop over patients...
    for patient in tqdm(patients_folders):
        new_id = old2new_idx[patient]
        current_path = os.path.join(datapath, patient, pattern_dicom_files)

        if os.path.isfile(os.path.join(datapath, patient, "new_id.txt")):
            new_id = open(os.path.join(datapath, patient, "new_id.txt")).read().splitlines()[0]
            old2set_idx[new_id] = patient.split("-")[-1]
            os.remove(os.path.join(datapath, patient, "new_id.txt"))

        # generate numeric string new ID - UI VR must have only digits
        #  use sha512 to be faster on 64 bits plaforms and supported by python 3.5
        new_id_numstr = str(int(hashlib.sha512(new_id.encode('UTF-8')).hexdigest(), base=16))[0:16]

        # List all files within patient folder...
        all_filenames = glob(current_path)

        # grab real birth date
        # TODO handle case where first file does not contain birthdate - look for any file that does?
        first_file = pydicom.read_file(all_filenames[0])
        if 'PatientBirthDate' in first_file:
            real_birthdate = first_file.data_element('PatientBirthDate').value
            fuzzed_birthdate = fuzz_date(real_birthdate)
        # print('Replacing real birthdate {} with {}'.format(real_birthdate, fuzzed_birthdate))
        else:
            fuzzed_birthdate = ""

        # Loop over all dicom files within a patient directory and anonymize them.
        for filename in all_filenames:

            path = os.path.normpath(filename)
            path = path.split(os.sep)

            if not os.path.isdir(os.path.join(output_folder, os.path.join(*path[-4:-3]))):
                os.mkdir(os.path.join(output_folder, os.path.join(*path[-4:-3])))

            if not os.path.isdir(os.path.join(output_folder, os.path.join(*path[-4:-2]))):
                os.mkdir(os.path.join(output_folder, os.path.join(*path[-4:-2])))

            if not os.path.isdir(os.path.join(output_folder, os.path.join(*path[-4:-1]))):
                os.mkdir(os.path.join(output_folder, os.path.join(*path[-4:-1])))

            anonymize_dicom_file(filename,
                                 os.path.join(output_folder, os.path.join(*path[-4:])),
                                 PatientID=new_id,
                                 PatientID_numstr=new_id_numstr,
                                 fuzzed_birthdate=fuzzed_birthdate,
                                 delete_identifiable_files=delete_identifiable_files)

        # If the patient folders are to be renamed.
        if rename_patient_directories:
            try:
                os.rename(os.path.join(output_folder, patient), os.path.join(output_folder, "sub-" + new_id))
            except OSError:
                os.rename(os.path.join(output_folder, patient), os.path.join(output_folder, "sub-" + new_id + "_2"))

    # return a mapping from new ids to old ids as a dictionary.
    new2old_idx = {new: old.replace("sub-", "") for old, new in old2new_idx.items()}

    # dumping new ids to a json file.
    with open(os.path.join(output_folder, 'mapper.json'), 'w') as fp:
        if len(old2set_idx.keys()) == 0:
            json.dump(new2old_idx, fp)
        else:
            json.dump(old2set_idx, fp)

    return new2old_idx


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("--in_folder", "-d", help="Directory to the dicom files to be anonymized.",
                        default=os.path.join(".", "data"), required=True)
    parser.add_argument("--out_folder", "-o", help="Output directory where the anonymized dicoms will be saved.",
                        default=os.path.join(".", "data"), required=True)
    parser.add_argument("--delete_identifiable", "-i", help="Delete identifiable files like Dose reports.",
                        default=False, required=False, action='store_true')
    parser.add_argument("--new_ids", "-n", help="List of new ids.")

    args = parser.parse_args()

    data_path = os.path.normcase(os.path.abspath(args.in_folder))
    output_folder = os.path.normcase(os.path.abspath(args.out_folder))
    delete_identifiable_files = args.delete_identifiable
    new_ids = args.new_ids

    if args.new_ids:
        new_ids = json.load(open(args.new_ids, "r"))

    if not os.path.isdir(output_folder):
        raise NotADirectoryError('Output directory does not exist. Please create it first.')

    # prevent deletion of identifiable files if output is the same as input dir
    if (data_path == output_folder) & delete_identifiable_files:
        warnings.warn('You have chosen in-place anonymisation with the delete-identifiable option. This is not'
                      'allowed since it could erase files in your in-folder. Please modify your options.')
    else:
        print("Anonymizing dicom files within path {}".format(os.path.abspath(data_path)))
        # Anonymizing all files.
        mapper = anonymize_all_dicoms_within_root_folder(output_folder=output_folder,
                                                         datapath=data_path,
                                                         new_ids=new_ids,
                                                         delete_identifiable_files=delete_identifiable_files)


if __name__ == "__main__":
    main(sys.argv[1:])
