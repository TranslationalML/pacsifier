import shutil
from glob import glob
import os
import sys
import argparse


def move(dicom_path: str, output_path: str) -> None:
    """Move all csv info files within a dicom directory into a new directory.

    Args:
            dicom_path: path to the folder containing dicoms.
            output_path: path where the csv files within the dicom path will be moved.

    """

    # List all csv files within the folder containing the dicom images.
    ls = glob(os.path.join(dicom_path, "sub-*", "ses-*", "*.csv"))

    # Iterate over all csv files paths.
    for l in ls:
        path = os.path.normpath(l)
        path = path.split(os.sep)

        # Create patient folder if not created yet.
        dir_ = output_path
        subfolder = os.path.join(dir_, path[-3])
        if not os.path.isdir(subfolder):
            os.mkdir(subfolder)

        # Create session folder if not created yet.
        subsubfolder = os.path.join(subfolder, path[-2])
        if not os.path.isdir(subsubfolder):
            os.mkdir(subsubfolder)

        # Move the csv file into the session folder.
        shutil.move(l, os.path.join(subsubfolder, path[-1]))

    if os.path.isfile(os.path.join(dicom_path, "mapper.json")):
        shutil.move(
            os.path.join(dicom_path, "mapper.json"),
            os.path.join(output_path, "mapper.json"),
        )


def get_parser() -> argparse.ArgumentParser:
    """Get parser for command line arguments."""
    parser = argparse.ArgumentParser(
        description="Move all csv files within a dicom folder into a new folder."
    )

    parser.add_argument("--data_folder", "-d", help="Path to the dicom folder")
    parser.add_argument(
        "--info_folder",
        "-o",
        help="Path to the folder where all csv files will be moved",
    )

    return parser


def main():
    """Main function of the script that calls :func:`move`."""
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # If there are missing arguments print help.
    if not args.data_folder or not args.info_folder:
        parser.print_help()
        sys.exit()

    dicom_path = args.data_folder
    output_path = args.info_folder

    # Move csv files within dicom_path within output_path
    move(dicom_path, output_path)


if __name__ == "__main__":
    main()
