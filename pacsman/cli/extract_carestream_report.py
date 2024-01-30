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

"""Script to extract plain text from Carestream radiology reports in SR."""

import io
import re
import os
import pydicom
from bs4 import BeautifulSoup
import argparse

__author__ = "Tommaso Di Noto, Jonas Richiardi"
__version__ = "0.0.3"
__email__ = "Tommaso.Di-Noto@chuv.ch"
__status__ = "Prototype"


def replace_special_char_combinations(input_report, print_clean_report=False) -> str:
    """This function corrects encoding errors that occur in the reports.

    Args:
        input_report (str): report that needs to be cleaned
        print_clean_report (bool): whether we want to print the cleaned report

    Returns:
        cleaned_report (str): clean report without encoding errors

    """
    cleaned_report = input_report.replace("\x91", "'")
    cleaned_report = cleaned_report.replace("\x92", "'")
    cleaned_report = cleaned_report.replace("\x96", "-")
    cleaned_report = cleaned_report.replace("\x9c", "oe")
    cleaned_report = cleaned_report.replace("Ã©", "é")
    cleaned_report = cleaned_report.replace("Ã¨", "è")
    cleaned_report = cleaned_report.replace("Â", " ")
    cleaned_report = cleaned_report.replace("Ã", "à")
    cleaned_report = cleaned_report.replace("Ã»", "û")
    cleaned_report = cleaned_report.replace("à»", "û")
    cleaned_report = cleaned_report.replace("Ã¯", "ï")
    cleaned_report = cleaned_report.replace("Ã«", "ë")
    cleaned_report = cleaned_report.replace("â€˜", "'")
    cleaned_report = cleaned_report.replace("â€™˜", "'")
    cleaned_report = cleaned_report.replace("â\x80\x99", "'")
    cleaned_report = cleaned_report.replace("à¯", "ï")
    cleaned_report = cleaned_report.replace("Ã¢", "â")
    cleaned_report = cleaned_report.replace("à¢", "â")
    cleaned_report = cleaned_report.replace("à´", "ô")

    if print_clean_report:  # if we want to print the cleaned report
        print(cleaned_report)

    return cleaned_report


def extract_txt_report(data_folder: str) -> None:
    """This function loops over a BIDS-like (Brain Imaging Data Structure) dataset.

    If some SRc files are found, it converts them to txt files and saves them in the same directory.

    Note:
        The function assumes that each subject is stored as ``~/.../sub-XXXXXX/ses-YYYYYYYYYYYYY/00001-CarestreamPACSReports/SRc.x.x.x``.

    Args:
        data_folder (str): path to BIDS-like dataset

    """
    # loop over all files inside specified folder
    for subdir, dirs, files in os.walk(data_folder):
        for file in files:
            if "SRc" in file:  # match filename for report
                parent_dir = os.path.dirname(
                    subdir
                )  # type: str  # save parent dir name
                grand_parent_dir = os.path.dirname(
                    parent_dir
                )  # type: str  # save grandparent dir name
                sub_nb = os.path.basename(
                    os.path.normpath(grand_parent_dir)
                )  # type: str  # save sub number
                ses_nb = os.path.basename(
                    os.path.normpath(parent_dir)
                )  # type: str  # save ses number
                print("\nCreating report for {}_{}".format(sub_nb, ses_nb))
                ds = pydicom.dcmread(
                    os.path.join(subdir, file)
                )  # type: pydicom.dataset.FileDataset()  # read dicom dataset (ds)

                if hasattr(ds, "SOPInstanceUID"):
                    SOP_Instance_UID_name = str(ds.SOPInstanceUID).replace(
                        ".", "_"
                    )  # type: str  # save SOP Instance UID for making the output file unique
                else:
                    raise ValueError("No SOPInstanceUID attribute found")

                # make sure that the input dicom file is a structured report, using the Modality dicom attribute
                if ds.Modality == "SR":
                    pass
                elif ds.Modality == "":
                    raise TypeError(
                        "Modality attribute, Tag (0008,0060), is empty, while it should be of type SR (Structured Report)."
                    )
                elif ds.Modality != "SR" and ds.Modality != "":
                    raise TypeError(
                        "Modality attribute, Tag (0008,0060), is not SR (Structured Report); this script is intended for SR dicom files."
                    )

                if hasattr(
                    ds, "ContentSequence"
                ):  # if the attribute ContentSequence exists
                    if hasattr(ds.ContentSequence, "_list"):
                        if (
                            len(ds.ContentSequence._list) >= 4
                        ):  # check if attribute "ContentSequence" exists
                            if hasattr(ds.ContentSequence._list[3], "ContentSequence"):
                                Potential_Text_Attribute = ds.ContentSequence._list[
                                    3
                                ].ContentSequence  # create candidate variable for extracting the report
                                if hasattr(
                                    Potential_Text_Attribute, "_list"
                                ):  # if attribute exists
                                    free_text = (
                                        ""
                                    )  # type: str  # initialize the variable to empty
                                    for idx, items in enumerate(
                                        Potential_Text_Attribute._list
                                    ):  # loop attributes until we find the Text Value attribute
                                        tmp = str(
                                            items
                                        )  # type: str  # temporary string variable
                                        if (
                                            "(0040, a160) Text Value" in tmp
                                        ):  # check if specific string matches in our temporary variable
                                            free_text = Potential_Text_Attribute._list[
                                                idx
                                            ].TextValue  # if it matches, save only Text Value content
                                            break  # terminate for loop since we found what we were looking for

                                    if (
                                        free_text == ""
                                    ):  # if the variable is still empty, raise error
                                        raise FileNotFoundError(
                                            "There is no Text Value attribute"
                                        )

                                soup = BeautifulSoup(
                                    free_text,
                                    from_encoding="utf-8",
                                    features="html.parser",
                                )  # type: BeautifulSoup  # create instance of BeautifulSoup class
                                cleaned_report = re.sub(
                                    r"[\n]+", r"\n", soup.text
                                )  # type: str  # remove white space (white lines) in excess

                                # replace special characters with corresponding actual value
                                cleaned_report = replace_special_char_combinations(
                                    cleaned_report, print_clean_report=False
                                )

                                # save report in same folder where the corresponding DCM-SR is
                                output_filename = (
                                    "Clean_Report_" + SOP_Instance_UID_name + ".txt"
                                )  # type: str
                                text_file = open(
                                    os.path.join(subdir, output_filename), "w"
                                )  # type: io.TextIOWrapper
                                text_file.write(
                                    cleaned_report
                                )  # save the report to disk
                                print("Report created and saved in {}".format(subdir))
                                text_file.close()
                            else:
                                print(
                                    "WATCH OUT: report not found for {}_{}. ContentSequence._list[3] has no attribute ContentSequence".format(
                                        sub_nb, ses_nb
                                    )
                                )
                        else:
                            print(
                                "WATCH OUT: report not found for {}_{}. ContentSequence_list has less than 4 elements".format(
                                    sub_nb, ses_nb
                                )
                            )
                    else:
                        print(
                            "WATCH OUT: report not found for {}_{}. ContentSequence has no attribute _list ".format(
                                sub_nb, ses_nb
                            )
                        )
                else:
                    print(
                        "WATCH OUT: report not found for {}_{}. ContentSequence attribute does not exist".format(
                            sub_nb, ses_nb
                        )
                    )


def get_parser() -> argparse.ArgumentParser:
    """Get parser object for command line arguments of the script.

    Note:
        It is assumed that each subject is stored as ``~/.../sub-XXXXXX/ses-YYYYYYYYYYYYY/00001-CarestreamPACSReports``.

    """
    parser = argparse.ArgumentParser(
        description="Extract plain text from Carestream radiology reports in SR."
    )

    parser.add_argument(
        "--data_folder",
        "-d",
        help="Path to the folder containing the reports",
        required=True,
    )

    return parser


def main():
    """Main function of the script that calls :func:`extract_txt_report`.

    Todo:
        - Add a parser to specify the `data_folder` as it is now hard-coded.

    """
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    data_folder = args.data_folder
    # data_folder = "/home/newuser/Downloads/tdn"  # type: str

    assert os.path.exists(data_folder), "Input path {} does not exist".format(
        data_folder
    )  # make sure path exists

    # invoke function to extract the reports as txt files
    extract_txt_report(data_folder)


if __name__ == "__main__":
    main()
