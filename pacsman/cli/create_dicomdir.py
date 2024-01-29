# Copyright (C) 2018-2024, University Hospital Center and University of Lausanne (UNIL-CHUV),
# Switzerland & Contributors, All rights reserved.
# This software is distributed under the open-source Apache 2.0 license.

"""Script to create a DICOMDIR of all dicoms within a folder."""

import os
import warnings
import argparse
import string
import random
from pacsman.core.execute_commands import run
from glob import glob
import shutil
from typing import Tuple, Dict, List

warnings.filterwarnings("ignore")

command = "dcmmkdir --recurse {}"
names = []


def generate_new_folder_name(names: List[str] = []) -> str:
    """Generate a folder/file name having between 4 and 8 characters of capital letters and digits.

    Args:
        names: new names already generated for other folders.

    Returns:
        str: Generated folder/file name.
    """
    generated = ""
    new_names = names + [""]

    # Make sure the name is not already used.
    while generated in new_names:
        N = random.randint(4, 8)
        generated = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
        )

    return generated


def add_or_retrieve_name(
    current_folder: str, old_2_new: Dict[str, str]
) -> Tuple[str, Dict[str, str]]:
    """Check if the current folder has had a generated new name. If that is the case, return its new name, otherwise, generate a new name.

    Args:
        current_folder: current folder to be considered
        old_2_new: dictionary keeping track of mapping between old and new folder / file names

    Returns:
        tuple: tuple containing the new name and the updated mapping between old and new name.

    """

    folder_name = None

    if current_folder not in old_2_new.keys():
        folder_name = generate_new_folder_name()
        old_2_new[current_folder] = folder_name
        names.append(folder_name)

    else:
        folder_name = old_2_new[current_folder]

    return folder_name, old_2_new


def move_and_rename_files(dicom_path: str, output_path: str) -> None:
    """Copy all the files within the dicom hierarchy into new hierarchy with appropriate names for DICOMDIR creation.

    Args:
        dicom_path: current folder to be considered
        output_path: path where the new dicom hierarchy will be stored

    """

    # List all dicom files paths.
    ls = glob(os.path.join(dicom_path, "sub-*", "ses-*", "*", "*"))
    old_2_new = {}

    # Iterating over dicom files
    for l in ls:
        path = os.path.normpath(l)
        path = path.split(os.sep)

        dir_ = output_path

        # Creating subject folder with 8 characters names.
        current_folder = path[-4]
        folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
        subfolder = os.path.join(dir_, folder_name)

        if not os.path.isdir(subfolder):
            os.mkdir(subfolder)

        # Creating session folder with 8 characters names.
        current_folder = path[-3]
        folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
        subsubfolder = os.path.join(subfolder, folder_name)

        if not os.path.isdir(subsubfolder):
            os.mkdir(subsubfolder)

        # Creating series folder with 8 characters names.
        current_folder = path[-2]
        folder_name, old_2_new = add_or_retrieve_name(current_folder, old_2_new)
        subsubsubfolder = os.path.join(subsubfolder, folder_name)

        if not os.path.isdir(subsubsubfolder):
            os.mkdir(subsubsubfolder)

        # Copying dicom files into the previously created series folder with 8 characters or less names.
        file_name = generate_new_folder_name(names=names)
        shutil.copyfile(l, os.path.join(subsubsubfolder, file_name))


def create_dicomdir(out_path: str) -> None:
    """Create a DICOMDIR of all dicoms with the path passed as parameter.

    Args:
        out_path: path of dicoms

    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # cd to the out_path
    os.chdir(os.path.abspath(out_path))

    # Executing the dcmmkdir command on current path
    run(command.format("./"))

    # Delete the log.txt file if it exists. (log.txt is supposed to be written in the same folder as the script after executing commands.
    # However, pointing to the out_path outputs log.txt in out_path. So, it is deleted.)
    if os.path.isfile("log.txt"):
        os.remove("log.txt")

    # Point back the script path.
    os.chdir(os.path.abspath(dir_path))


def get_parser() -> argparse.ArgumentParser:
    """Get parser object for command line arguments of the script."""
    parser = argparse.ArgumentParser(
        description="Create a DICOMDIR of all dicoms within a folder."
    )

    parser.add_argument(
        "--in_folder",
        "-d",
        help="Directory to the dicom files",
        default=os.path.join(".", "data"),
    )
    parser.add_argument(
        "--out_folder",
        "-o",
        help="Output directory where the dicoms and DICOMDIR will be saved",
        default=os.path.join(".", "data"),
    )

    return parser


def main():
    """Main function of the script that calls :func:`move_and_rename_files` and :func:`create_dicomdir`."""
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    in_path = args.in_folder
    out_path = args.out_folder

    # Copying the files within in_path into out_path with new names.
    move_and_rename_files(in_path, out_path)

    # Creating the DICOMDIR within the out_path.
    create_dicomdir(out_path)


if __name__ == "__main__":
    main()
