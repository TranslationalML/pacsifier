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

"""Script to query, retrieve, and upload DICOM images from / to a PACS server."""

import re
import shutil
import unicodedata
import sys
from tqdm import tqdm
import os
import warnings
from pandas import read_csv, DataFrame
import json
from typing import Iterator, Dict, List
from cerberus import Validator
import csv
import time
import argparse

from pacsman.core.execute_commands import echo, find, get, move_remote, write_file
from pacsman.core.sanity_checks import (
    check_date,
    check_date_range,
    check_query_attributes,
    check_config_file,
)

warnings.filterwarnings("ignore")

TAG_TO_KEYWORD = {  # type: Dict[str,str]
    "(0008,0020)": "StudyDate",
    "(0008,0030)": "StudyTime",
    "(0008,103e)": "SeriesDescription",
    "(0010,0020)": "PatientID",
    "(0018,1030)": "ProtocolName",
    "(0020,000d)": "StudyInstanceUID",
    "(0020,000e)": "SeriesInstanceUID",
    "(0010,0010)": "PatientName",
    "(0010,0030)": "PatientBirthDate",
    "(0018,1000)": "DeviceSerialNumber",
    "(0008,0022)": "AcquisitionDate",
    "(0008,0060)": "Modality",
    "(0008,0008)": "ImageType",
    "(0020,0011)": "SeriesNumber",
    "(0008,1030)": "StudyDescription",
    "(0008,0050)": "AccessionNumber",
    "(0018,0024)": "SequenceName",
}

ALLOWED_FILTERS = list(TAG_TO_KEYWORD.values())
ALLOWED_FILTERS.append("new_ids")


def readLineByLine(filename: str) -> Iterator[str]:
    """Return a list of lines of a text file located at the path filename.

    Args:
        filename: path to text file to be read

    Yields:
        Iterator: list of text lines of the file

    """
    with open(filename, "r", encoding="utf_8") as f:
        for line in f:
            line = line.encode("ascii", "ignore").decode("ascii")
            yield line.strip("\n")


def parse_findscu_dump_file(filename: str) -> List[Dict[str, str]]:
    """Extract all useful information from the text file generated by dumping the output of the findscu command.

    Args:
        filename: path to textfile to be read

    Returns:
        list: list dictionaries each containing the attributes of a series

    """
    start = False

    id_table = []  # type: List[str]
    output_dict = {"": ""}  # type: Dict[str,str]

    # Iterate over text lines
    for line in readLineByLine(filename):
        sample_dict = {  # type: Dict[str,str]
            "StudyDate": "",
            "StudyTime": "",
            "SeriesDescription": "",
            "PatientID": "",
            "ProtocolName": "",
            "StudyInstanceUID": "",
            "PatientName": "",
            "PatientBirthDate": "",
            "SeriesInstanceUID": "",
            "DeviceSerialNumber": "",
            "Modality": "",
            "ImageType": "",
            "SeriesNumber": "",
            "StudyDescription": "",
            "AccessionNumber": "",
            "SequenceName": "",
        }

        if "------------" in line or "Releasing Association" in line:
            if start:
                id_table.append(output_dict)

            start = True
            output_dict = sample_dict
            continue

        if not start:
            continue
        for tag in sorted(TAG_TO_KEYWORD.keys()):
            # if current line contains a given tag then extract information from it.
            if tag in line:
                item = ""
                try:
                    item = (
                        line.split("[")[1]
                        .split("]")[0]
                        .replace(" ", "")
                        .replace("'", "_")
                        .replace("/", "")
                    )
                # In case line.split gives a list of length less that 4 pass to next line.
                except IndexError:
                    pass

                if item == "(no":
                    continue
                output_dict[TAG_TO_KEYWORD[tag]] = item

    return id_table


def check_query_table_allowed_filters(
    table: DataFrame, allowed_filters: List[str] = ALLOWED_FILTERS
) -> None:
    """Check if the csv table passed as input has only attributes that are allowed.

    Args:
        table: table containing all filters
        allowed_filters: list of allowed attribute names

    """
    cols = table.columns
    for col in cols:
        if col not in allowed_filters:
            raise ValueError(
                "Attribute "
                + col
                + " not allowed! Please check the input table's column names."
            )

    return


def parse_query_table(
    table: DataFrame, allowed_filters: List[str] = ALLOWED_FILTERS
) -> List[Dict[str, str]]:
    """Take the query table passed as input to the script and parse it using attributes in the query / retrieve command.

    Args:
        table: input csv table
        allowed_filters: list of allowed attributes to be filtered

    Returns:
        list: list of dictionaries each containing the corresponding value of each attribute in allowed_filters
            (in the case an attribute has no corresponding column in the csv table, an empty string is given)

    """
    attributes_list = []
    for idx in table.index:
        # Initializing item dictionary.
        filter_dictionary = {filter_: "" for filter_ in allowed_filters}

        for col in table.columns:
            filter_dictionary[col] = table.loc[idx, col]

        attributes_list.append(filter_dictionary)

    return attributes_list


def process_person_names(name: str) -> str:
    """Modify patient name for the query input.

    It convert all characters to uppercase, prepends a ``*``
    to the last name and returns the new name.

    Args:
        name: patient's name

    Returns:
        string: patient name in the format it will be used in the query

    """
    if name == "":
        return ""
    splitted_name = name.upper().split(" ")
    new_name = "*" + splitted_name[-1]
    return new_name


def retrieve_dicoms_using_table(
    table: DataFrame,
    parameters: Dict[str, str],
    output_dir: str,
    save: bool,
    info: bool,
    move: bool,
) -> None:
    """Query and retrieve dicom images or / and  their info dumps using the input query table.

    Args:
        table: query table
        parameters: query/retrieve parameters
        output_dir: path to the output directory
        save: option to save the images
        info: option to save info dumps

    """
    pacs_server = parameters["server_address"]
    port = int(parameters["port"])
    move_port = int(parameters["move_port"])
    client_aet = parameters["AET"]
    server_aet = parameters["server_AET"]
    move_aet = parameters["move_AET"]
    batch_wait_time = int(parameters["batch_wait_time"])
    batch_size = int(parameters["batch_size"])

    # Flexible parsing.
    attributes_list = parse_query_table(table, ALLOWED_FILTERS)

    schema = {
        "PatientID": {"type": "string", "maxlength": 64},
        "StudyDate": {"type": "string", "maxlength": 17},
        "StudyInstanceUID": {"type": "string", "maxlength": 64},
        "SeriesInstanceUID": {"type": "string", "maxlength": 64},
        "ProtocolName": {"type": "string", "maxlength": 64},
        "PatientName": {"type": "string", "maxlength": 64},
        "SeriesDescription": {"type": "string", "maxlength": 64},
        "AcquisitionDate": {"type": "string", "maxlength": 8},
        "PatientBirthDate": {"type": "string", "maxlength": 8},
        "DeviceSerialNumber": {"type": "string", "maxlength": 64},
        "Modality": {"type": "string", "maxlength": 16},
        "SeriesNumber": {"type": "string", "maxlength": 12},
        "StudyDescription": {"type": "string", "maxlength": 64},
        "AccessionNumber": {"type": "string", "maxlength": 16},
        "SequenceName": {"type": "string", "maxlength": 64}
        # "ImageType" 		: {'type': 'string', 'maxlength': 16} The norm says it is a CS but apparently it is something else on Chuv PACS server.
    }

    validator = Validator(schema)
    counter = 0
    for i, query_attributes in enumerate(attributes_list):
        # print("Retrieving images for element number ", i+1)

        check_query_attributes(query_attributes)

        query_attributes["PatientName"] = process_person_names(query_attributes["PatientName"])

        if len(query_attributes["StudyDate"]) > 0:
            print(
                "Retrieving images for element number {0}: sub-{1}_ses-{2}".format(
                    i + 1, query_attributes["PatientID"], query_attributes["StudyDate"]
                )
            )
        else:
            print(
                "Retrieving images for element number {0}: sub-{1}".format(
                    i + 1, query_attributes["PatientID"]
                )
            )

        inputs = {k: query_attributes[k] for k in schema.keys()}

        if not validator.validate(inputs):
            raise ValueError(
                "Invalid input file element at position  "
                + str(i)
                + " "
                + str(validator.errors)
            )

        check_date_range(query_attributes["StudyDate"])
        check_date_range(query_attributes["AcquisitionDate"])
        check_date(query_attributes["PatientBirthDate"])

        query_retrieval_level = "SERIES"
        if query_attributes["ImageType"] != "":
            query_retrieval_level = "IMAGE"

        # check if we can ping the PACS
        echo_res = echo(
            server_address=pacs_server,
            port=port,
            server_aet=server_aet,
            aet=client_aet,
            log_dir=os.path.join(output_dir, "logs"),
        )
        if not echo_res:
            raise RuntimeError(
                "Cannot associate with PACS server. Please check connectivity and firewall settings"
                " with respect to ports configured in your config file."
            )

        # Look for series of current patient and current study.
        find_series_res = find(
            client_aet,
            server_address=pacs_server,
            server_aet=server_aet,
            port=port,
            query_retrieval_level=query_retrieval_level,
            patient_id=query_attributes["PatientID"],
            study_uid=query_attributes["StudyInstanceUID"],
            series_instance_uid=query_attributes["SeriesInstanceUID"],
            series_description=query_attributes["SeriesDescription"],
            protocol_name=query_attributes["ProtocolName"],
            acquisition_date=query_attributes["AcquisitionDate"],
            study_date=query_attributes["StudyDate"],
            patient_name=query_attributes["PatientName"],
            patient_birthdate=query_attributes["PatientBirthDate"],
            device_serial_number=query_attributes["DeviceSerialNumber"],
            modality=query_attributes["Modality"],
            image_type=query_attributes["ImageType"],
            study_description=query_attributes["StudyDescription"],
            accession_number=query_attributes["AccessionNumber"],
            sequence_name=query_attributes["SequenceName"],
            log_dir=os.path.join(output_dir, "logs"),
        )

        current_findscu_dump_file = os.path.join(output_dir, "tmp", "current.txt")
        if os.path.isfile(current_findscu_dump_file):
            os.remove(current_findscu_dump_file)

        write_file(find_series_res, file=current_findscu_dump_file)

        # Extract all series StudyInstanceUIDs etc.
        series = parse_findscu_dump_file(current_findscu_dump_file)

        # Pre-compile sanitizing regex for folder renaming
        my_re_clean = re.compile("[^0-9a-zA-Z]+")  # keep only alphanums

        # loop over series
        for serie in tqdm(series):
            # replace illegal chars with underscores
            patientID_sanitized = my_re_clean.sub(
                "_",
                unicodedata.normalize("NFD", serie["PatientID"])
                .encode("ascii", "ignore")
                .decode("ascii"),
            )

            # TODO handle empty patientID_sanitized
            if patientID_sanitized == "":
                patientID_sanitized = my_re_clean.sub(
                    "_",
                    unicodedata.normalize("NFD", query_attributes["PatientID"])
                    .encode("ascii", "ignore")
                    .decode("ascii"),
                )

            counter += 1
            if counter % batch_size == 0:
                time.sleep(batch_wait_time)

            patient_dir = os.path.join(output_dir, "sub-" + patientID_sanitized)

            # Make the patient folder.
            # if not os.path.isdir(patient_dir) and (save or info):
            #     print("Creating directory " + patient_dir)
            #     os.makedirs(patient_dir, exist_ok=True)

            if query_attributes["new_ids"] != "":
                with open(os.path.join(patient_dir, "new_id.txt"), "w") as file:
                    file.write(str(query_attributes["new_ids"]))

            # Make a session folder for the study if the StudyDate and StudyTime are not empty
            if len(serie["StudyDate"]) > 0 and len(serie["StudyTime"]) > 0:
                patient_study_output_dir = os.path.join(
                    patient_dir, f'ses-{serie["StudyDate"] + serie["StudyTime"]}'
                )
                # if not os.path.isdir(patient_study_output_dir) and (save or info):
                #     os.makedirs(patient_study_output_dir, exist_ok=True)
            elif len(serie["StudyDate"]) > 0:
                patient_study_output_dir = os.path.join(
                    patient_dir, f'ses-{serie["StudyDate"]}'
                )
            else:
                patient_study_output_dir = os.path.join(patient_dir)

            # Make the patient / session folders if they don't exist.
            if save or info:
                os.makedirs(patient_study_output_dir, exist_ok=True)

            # Name the series folder after the SeriesDescription.
            folder_name = serie["SeriesDescription"]

            # Pre-emptively sanitize the folder name - decompose into separate combining chars, then remove them using asci encoding-decoding.
            # finally replace illegal chars with underscores
            folder_name = my_re_clean.sub(
                "_",
                unicodedata.normalize("NFD", folder_name)
                .encode("ascii", "ignore")
                .decode("ascii"),
            )

            # If the StudyDescription is an empty string name the folder No_series_description.
            if folder_name == "":
                folder_name = "No_series_description"
            patient_serie_output_dir = os.path.join(
                patient_study_output_dir,
                serie["SeriesNumber"].zfill(5) + "-" + folder_name,
            )

            # Store all later retrieved files of current patient within the serie_id directory.
            if not os.path.isdir(patient_serie_output_dir) and (save or info):
                os.makedirs(patient_serie_output_dir, exist_ok=True)

            # Retrieving files of current patient, study and serie.
            # TODO: handle and report error 'F: cannot listen on port 104, insufficient privileges' in movescu
            if save:
                get_res = get(
                    client_aet,
                    query_attributes["StudyDate"],  # serie["StudyDate"],
                    server_address=pacs_server,
                    server_aet=server_aet,
                    port=port,
                    patient_id=query_attributes["PatientID"],  # serie["PatientID"],
                    study_instance_uid=serie["StudyInstanceUID"],
                    series_instance_uid=serie["SeriesInstanceUID"],
                    move_port=move_port,
                    output_dir=patient_serie_output_dir,
                    log_dir=os.path.join(output_dir, "logs"),
                )

            if move:
                move_res = move_remote(
                    client_aet,
                    query_attributes["StudyDate"],  # serie["StudyDate"],
                    server_address=pacs_server,
                    server_aet=server_aet,
                    port=port,
                    patient_id=query_attributes["PatientID"],  # serie["PatientID"],
                    study_instance_uid=serie["StudyInstanceUID"],
                    series_instance_uid=serie["SeriesInstanceUID"],
                    move_aet=move_aet,
                    log_dir=os.path.join(output_dir, "logs"),
                )

            if info:
                # Writing series info to csv file.
                with open(patient_serie_output_dir + ".csv", "w") as f:
                    w = csv.DictWriter(f, serie.keys())
                    w.writeheader()
                    w.writerow(serie)

            if os.path.isfile(current_findscu_dump_file):
                os.remove(current_findscu_dump_file)
    
    # Clean the tmp folder
    if os.path.isdir(os.path.join(output_dir, "tmp")):
        shutil.rmtree(os.path.join(output_dir, "tmp"), ignore_errors=True)    


def get_parser() -> argparse.ArgumentParser:
    """Return the parser object for this script."""
    parser = argparse.ArgumentParser(
        description="Query, move and retrieve DICOM images from a PACS server."
    )

    parser.add_argument(
        "--config",
        "-c",
        help="Configuration file path",
        default=os.path.join(".", "files", "config.json"),
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Store images resulting from query (cannot be used together with '--move')",
    )
    parser.add_argument(
        "--info",
        "-i",
        action="store_true",
        help="Store parsed version of findscu output (DICOM header subset)",
    )
    parser.add_argument(
        "--move",
        "-m",
        action="store_true",
        help="Move images resulting from query (cannot be used together with '--save')",
    )
    parser.add_argument("--queryfile", "-q", help="Path to query file")
    parser.add_argument(
        "--out_directory",
        "-d",
        help="Output directory where images will be saved",
        default=os.path.join(".", "data"),
    )

    return parser


def main():
    """Main function of the script that calls :func:`retrieve_dicoms_using_table`."""
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    config_path = args.config
    save = args.save
    info = args.info
    move = args.move

    # Reading config file.
    try:
        with open(config_path) as f:
            parameters = json.load(f)
        check_config_file(parameters)
    except FileNotFoundError:
        args.config = None
        pass

    output_dir = args.out_directory

    # Check the case where save & move are specified (it should be only one of the two)
    if args.save and args.move:
        print(
            "You must select either '--save' to save locally or '--move' to define a remote destination, not both!"
        )
        parser.print_help()
        sys.exit()

    # Check the case where the queryfile option is missing. If it is the case print help.
    if args.queryfile is None or args.config is None:
        print("Missing mandatory parameter --queryfile or --config!")
        parser.print_help()
        sys.exit()

    # Read the query file.
    table = read_csv(args.queryfile, dtype=str).fillna("")

    check_query_table_allowed_filters(table)

    retrieve_dicoms_using_table(table, parameters, output_dir, save, info, move)


if __name__ == "__main__":
    main()
