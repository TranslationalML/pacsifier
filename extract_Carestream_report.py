#!/usr/bin/env python

"""
Given Carestream radiology reports in SR, extract plain text.

This is part of PACSMAN, a batch PACS query tool under development at CHUV

"""

import io
import re
import os
import pydicom
from bs4 import BeautifulSoup

__author__ = "Tommaso Di Noto, Jonas Richiardi"
__version__ = "0.0.1"
__email__ = "Tommaso.Di-Noto@chuv.ch"
__status__ = "Prototype"

# N.B. we assume that each subject is stored as ~/.../sub-XXXXXX/ses-YYYYYYYYYYYYY/00001-CarestreamPACSReports
data_path = "path/to/folder/where/subs/are/stored"  # type: str

assert os.path.exists(data_path), "Input path {0} does not exist".format(data_path)

# loop over all files inside specified folder
for subdir, dirs, files in os.walk(data_path):
    for file in files:
        if "SRc" in file:  # match filename for report
            if "20190605130930" in subdir:
                print()
            parent_dir = os.path.dirname(subdir)  # type: str  # save parent dir name
            grand_parent_dir = os.path.dirname(parent_dir)  # type: str  # save grandparent dir name
            sub_nb = os.path.basename(os.path.normpath(grand_parent_dir))  # type: str  # save sub number
            ses_nb = os.path.basename(os.path.normpath(parent_dir))  # type: str  # save ses number
            print("\nCreating report for {0}_{1}".format(sub_nb, ses_nb))
            ds = pydicom.dcmread(os.path.join(subdir, file))  # type: pydicom.dataset.FileDataset()  # read dicom dataset (ds)

            SOP_Instance_UID_name = str(ds.SOPInstanceUID).replace(".", "_")  # type: str  # save SOP Instance UID for making the output file unique

            # make sure that the input dicom file is a structured report, using the Modality dicom attribute
            if ds.Modality == "SR":
                pass
            elif ds.Modality == "":
                raise TypeError("Modality attribute, Tag (0008,0060), is empty, while it should be of type SR (Structured Report).")
            elif ds.Modality != "SR" and ds.Modality != "":
                raise TypeError("Modality attribute, Tag (0008,0060), is not SR (Structured Report); this script is intended for SR dicom files.")

            Potential_Text_Attribute = ds.ContentSequence._list[3].ContentSequence  # create candidate variable for extracting the report

            if hasattr(Potential_Text_Attribute, "_list"):  # if attribute exists
                free_text = ""  # type: str  # initialize the variable to empty
                for idx, items in enumerate(Potential_Text_Attribute._list):  # loop attributes until we find the Text Value attribute
                    tmp = str(items)  # type: str  # temporary string variable
                    if "(0040, a160) Text Value" in tmp:  # check if specific string matches in our temporary variable
                        free_text = Potential_Text_Attribute._list[idx].TextValue  # if it matches, save only Text Value content
                        break  # terminate for loop since we found what we were looking for

                if free_text == "":  # if the variable is still empty, raise error
                    raise FileNotFoundError("There is no Text Value attribute")

            soup = BeautifulSoup(free_text, from_encoding="utf-8", features="html.parser")  # type: BeautifulSoup  # create instance of BeautifulSoup class
            cleaned_soup = re.sub(r'[\n]+', r'\n', soup.text)  # type: str  # remove white space (white lines) in excess

            # replace special characters with corresponding actual value
            cleaned_soup = cleaned_soup.replace("\x91", "'")
            cleaned_soup = cleaned_soup.replace("\x92", "'")
            cleaned_soup = cleaned_soup.replace("\x96", "-")
            cleaned_soup = cleaned_soup.replace("\x9c", "oe")
            cleaned_soup = cleaned_soup.replace("Ã©", "é")
            cleaned_soup = cleaned_soup.replace("Ã¨", "è")
            cleaned_soup = cleaned_soup.replace("Â", " ")
            cleaned_soup = cleaned_soup.replace("Ã", "à")
            cleaned_soup = cleaned_soup.replace("Ã»", "û")
            cleaned_soup = cleaned_soup.replace("à»", "û")
            cleaned_soup = cleaned_soup.replace("Ã¯", "ï")
            cleaned_soup = cleaned_soup.replace("Ã«", "ë")
            cleaned_soup = cleaned_soup.replace("â€˜", "'")
            cleaned_soup = cleaned_soup.replace("â€™˜", "'")
            cleaned_soup = cleaned_soup.replace("â\x80\x99", "'")
            cleaned_soup = cleaned_soup.replace("à¯", "ï")
            cleaned_soup = cleaned_soup.replace("Ã¢", "â")
            cleaned_soup = cleaned_soup.replace("à¢", "â")


            #print(cleaned_soup)  # uncomment this line to display cleaned extracted report

            # save report in same folder where the corresponding DCM-SR is
            output_filename = "Clean_Report_" + SOP_Instance_UID_name + ".txt"  # type: str
            text_file = open(os.path.join(subdir, output_filename), "w")  # type: io.TextIOWrapper
            text_file.write(cleaned_soup)
            print("Report created and saved in {0}".format(subdir))
            text_file.close()
