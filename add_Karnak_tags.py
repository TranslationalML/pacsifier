"""
Add private DICOM tags to several studies so that Karnak can de-identify them using provided patient codes
and route them to the appropriate Kheops album
"""

import pydicom
from glob import glob
import sys
import os
from tqdm import tqdm
import json
from typing import Dict
import argparse


def tag_dicom_file(
        filename: str,
        patient_code: str,
        patient_shift: str,
        album_name: str,
) -> None:
    """
    Tags the dicom image located at filename by adding patient code and Kheops album name to private tags for
    subsequent de-identification

    Args :
        filename: path to dicom image.
        patient_code: pseudonymous patient code
        album_name: Kheops album name
    """

    # Load the current dicom file to 'deidentify'
    try:
        dataset = pydicom.read_file(filename)
    except pydicom.errors.InvalidDicomError as e:
        print("Dicom Error at file at path :  " + filename)
        print(e)

    block = dataset.private_block(0x000b, "CHUV_DEV_TML", create=True)
    block.add_new(0x01, "LO", patient_code) # Patient Code
    block.add_new(0x02, "LO", album_name) # Album name
    block.add_new(0x03, "LO", patient_shift) # Day shift per patient

    # write the modified DICOM
    dataset.save_as(filename)


def tag_all_dicoms_within_root_folder(*,
                                      data_path: str,
                                      new_ids: Dict[str, str],
                                      day_shift : Dict[str, str],
                                      album_name: str
                                      ) -> None:
    """
    Tags all dicom images located at the datapath for Karnak, adding an album name and patientCode private tags.
    Args :
        data_path: The path to the dicom images.
        new_ids: The real:code mapping to be used after de-identifying the original ids.
        album_name : The name of the Kheops album
    """

    pattern_dicom_files = os.path.join("ses-*", "*", "*")

    # List all  patient directories.
    patients_folders = next(os.walk(data_path))[1]

    if not patients_folders:
        raise NotADirectoryError('Each patient should have their own directory under the provided root ' + data_path)

    if new_ids is None:
        raise ValueError("Must provide a dictionary mapping real to coded patientID")

    if album_name is None:
        raise ValueError("Must provide non-empty Kheops album name")

    # Keep a mapping from old to new ids in a dictionary.
    old2new_idx = {patients_folders[i]: new_ids[patients_folders[i]] for i in range(len(patients_folders))}
    personal_day_shift = {patients_folders[i]: (day_shift[patients_folders[i]] if patients_folders[i] in day_shift else 0) for i in range(len(patients_folders))}

    # TODO add Cerberus validation on album_name and newid - both should be DICOM VR LO

    # Loop over patients...
    for patient in tqdm(patients_folders):
        new_id = old2new_idx[patient]
        patient_shift = personal_day_shift[patient]
        current_path = os.path.join(data_path, patient, pattern_dicom_files)

        # List all files within patient folder
        all_filenames = glob(current_path)

        if not all_filenames:
            raise FileNotFoundError('Patient directories are expect to conform to the quasi-BIDS organisation '
                                    'sub-XXX/ses-YYY/')

        # List all study dirs for this patient.
        study_dirs = next(os.walk(os.path.join(data_path, patient)))[1]

        for study_dir in study_dirs:

            # List all series dirs for this patient.
            series_dirs = next(os.walk(os.path.join(data_path, patient, study_dir)))[1]

            for series_dir in series_dirs:

                all_filenames_series = glob(os.path.join(data_path, patient, study_dir,series_dir,'*'))

                # Loop over all dicom files within a patient directory and anonymize them.
                for filename in all_filenames_series:
                    tag_dicom_file(os.path.join(data_path, patient, study_dir, series_dir,
                                                os.path.basename(filename)),
                                   patient_code=new_id,
                                   patient_shift=patient_shift,
                                   album_name=album_name)


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("--in_folder", "-d", help="Directory to the dicom files.",
                        default=os.path.join(".", "data"), required=True)
    parser.add_argument("--new_ids", "-n", help="List of new patient IDentifiers.", required=True)
    parser.add_argument("--day_shift", "-s", help="List of day shift per patient.", required=False)
    parser.add_argument("--album_name", "-a", help="Name of destination Kheops album to route the tagged study",
                        required=True)

    args = parser.parse_args()

    data_path = os.path.normcase(os.path.abspath(args.in_folder))
    album_name = args.album_name
    new_ids = json.load(open(args.new_ids, "r"))
    if args.day_shift is not None:
        day_shift = json.load(open(args.day_shift, "r"))
    else:
        day_shift = {}

    if not os.path.isdir(data_path):
        raise NotADirectoryError('Input directory does not exist. Please check.')

    print("Tagging DICOM files within path {}".format(data_path))

    tag_all_dicoms_within_root_folder(data_path=data_path,
                                      new_ids=new_ids,
                                      day_shift=day_shift,
                                      album_name=album_name)


if __name__ == "__main__":
    main(sys.argv[1:])
