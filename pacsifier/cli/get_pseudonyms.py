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

"""Script to get the new pseudonyms and day shifts in JSON format.

The script can be used in two modes:
- de-id: use the de-ID API to get new pseudonyms and day shifts
- custom: use a custom mapping file in CSV format that specifies the mapping of old / new pseudonyms

In case of the de-id mode, the script requires a PACSIFIER query file and a configuration file for the de-ID API.
In case of the custom mode, the script requires a custom mapping file in CSV format.

The script saves the new pseudonyms and day shifts as JSON files in the specified output directory.

Example usage:
    python get_pseudonyms.py --mode de-id --config config.json --queryfile query.csv --project_name PACSIFIERCohort --out_directory /path/to/output
    python get_pseudonyms.py --mode custom --mappingfile mapping.csv --shift-days --project_name PACSIFIERCohort --out_directory /path/to/output

"""

import ast
import sys, os, argparse
import json, csv, requests
from typing import Dict, Any
import numpy as np
from pandas import read_csv
from pacsifier.cli.pacsifier import check_query_table_allowed_filters


def check_config_file_deid(config_file: Dict[str, str]) -> None:
    """Check that the config file passed as a parameter is valid.

    Args:
        config_file: dictionary loaded from the config json file

    """
    items = set(config_file.keys())
    valid_keys = ["deid_URL", "deid_token"]
    if items != set(valid_keys):
        raise ValueError(
            "Invalid config file! Must contain these and only these keys: "
            + " ".join(valid_keys)
        )


def convert_csv_to_deid_json(queryfile: str, project_name: str) -> Any:
    """Convert PACSIFIER query to json format the de-ID API can understand.

    Args:
        queryfile: the filename of the PACSIFIER query file
        project_name: the name of the project in GPCR (may or may not correspond to Kheops album)

    Returns:
        JSON object suitable for the API

    """
    json_new_str = '{"project": "' + project_name + '", "PatientIDList": ['
    patient_list_str = ""

    with open(queryfile, newline="",encoding='UTF-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["PatientID"] != "":
                patient_list_str = (
                    patient_list_str + '{"PatientID": "' + row["PatientID"] + '"}, '
                )

    if len(patient_list_str) > 0:
        if patient_list_str.endswith(", "):
            patient_list_str = patient_list_str[:-2]
        json_new_str = json_new_str + patient_list_str + "]}"
    else:
        json_new_str = "{}"

    return json.loads(json_new_str)


def get_deid_pseudonyms(deid_parameters: dict, query_json: dict) -> None:
    """Run the de-ID request and return the response as a json.

    Args:
        deid_parameters: dictionary containing the de-ID URL and token in the following format::

            {
                "deid_URL": "https://dummy.url.example",
                "deid_token": "1234567890"
            }

        query_json: the PACSIFIER query formatted as a dictionary

    Returns:
        JSON object containing the new pseudonyms for each patient

    """
    head = {"Authorization": f'token {deid_parameters["deid_token"]}'}

    response = requests.post(
        deid_parameters["deid_URL"], headers=head, json=query_json, verify=False
    )

    resp = ast.literal_eval(response.text)
    json_resp = json.dumps(resp, indent=4)

    return json_resp


def get_deid_day_shifts(deid_parameters: dict, query_json: dict) -> None:
    """Run the de-ID request for day shifts and return the response as a json.

    Args:
        deid_parameters: dictionary containing the de-ID URL and token in the following format::

            {
                "deid_URL": "https://dummy.url.example",
                "deid_token": "1234567890"
            }

        query_json: the PACSIFIER query formatted as a dictionary

    Returns:
        JSON object containing the day shifts for each patient

    """
    head = {"Authorization": f'token {deid_parameters["deid_token"]}'}

    response = requests.post(
        deid_parameters["deid_URL"] + "_shift",
        headers=head,
        json=query_json,
        verify=False,
    )

    resp = ast.literal_eval(response.text)
    
    #force day shift in integer for tml compatibility (if provided in str)
    for key in resp.keys():
        resp[key] = int(resp[key])
    
    json_resp = json.dumps(resp, indent=4)

    return json_resp


def check_queryfile_content(queryfile: str) -> None:
    """Check that the PACSIFIER query file is valid.

    Args:
        queryfile: the path of the PACSIFIER query file

    """
    try:
        query_table = read_csv(queryfile, dtype=str).fillna("")
    except Exception as e:
        print(f"Error reading PACSIFIER query file: {e}")
        sys.exit(1)

    check_query_table_allowed_filters(query_table)


def get_parser() -> argparse.ArgumentParser:
    """Get parser for command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create new pseudonyms for a list of PatientIDs."
    )

    parser.add_argument(
        "--mode",
        "-m",
        help='Mode of operation: use de-ID API to get new pseudonyms and day shifts ("de-id") '
        'or use a custom mapping file in CSV format that specifies the new pseudonyms ("custom")',
        choices=["de-id", "custom"],
        default="de-id",
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Deidentification configuration file path (required for --mode de-id)",
        required="--mode de-id" in sys.argv,
    )
    parser.add_argument(
        "--queryfile",
        "-q",
        help="Path to PACSIFIER query file (used to find PatientIDs, required for --mode de-id)",
        required="--mode de-id" in sys.argv,
    )
    parser.add_argument(
        "--mappingfile",
        "-mf",
        help="Path to custom mapping file in CSV format (required for --mode custom). "
        "The file is expected to have no header and two columns: the first column is the old pseudonym, "
        "the second column is the new pseudonym. The file should not contain any empty cells.",
        required="--mode custom" in sys.argv,
    )
    parser.add_argument(
        "--shift-days",
        action="store_true",
        help="Generate random day shifts for all pseudonyms in the +- 30 days range (employed for --mode custom). "
        "If not specified, day shifts are set to 0.",
    )
    parser.add_argument(
        "--project_name",
        "-a",
        help="Name of the project in GPCR (may or may not correspond to Kheops album)",
        required=True,
    )
    parser.add_argument(
        "--out_directory",
        "-d",
        help="Output directory where the pseudonyms will be saved as a json",
        required=True,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Print verbose output",
        action="store_true",
    )

    return parser


def main():
    """Main function of the script."""
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # Check if the output directory exists. If not, create it.
    output_dir = os.path.abspath(args.out_directory)
    if not os.path.isdir(output_dir):
        print(f"Output directory does not exist! Creating {output_dir}...")
        os.makedirs(output_dir, exist_ok=True)

    if args.mode == "de-id":
        # Check if the config file exists.
        config_path = os.path.abspath(args.config)
        if not os.path.isfile(config_path):
            print(f"Config file {config_path} does not exist!")
            sys.exit(1)

        # Read and validate config file for deid parameters.
        with open(config_path) as f:
            try:
                deid_parameters = json.load(f)
            except json.JSONDecodeError:
                print("The config file does not contain valid json.")
                sys.exit(1)

            check_config_file_deid(deid_parameters)

        # Check if the queryfile exists.
        query_file = os.path.abspath(args.queryfile)
        if not os.path.isfile(query_file):
            print(f"Query file {query_file} does not exist!")
            sys.exit(1)

        # Validate the queryfile content.
        check_queryfile_content(query_file)

        # Convert the queryfile to json format.
        deid_query_json = convert_csv_to_deid_json(query_file, args.project_name)

        # Get the new pseudonyms
        json_pseudo_response = get_deid_pseudonyms(deid_parameters, deid_query_json)

        # Get day shift
        json_day_shift_response = get_deid_day_shifts(deid_parameters, deid_query_json)

    else:
        # Read the custom mapping file.
        mappingfile_path = os.path.abspath(args.mappingfile)
        if not os.path.isfile(mappingfile_path):
            print(f"Custom mapping file {mappingfile_path} does not exist!")
            sys.exit(1)

        mapping_table = read_csv(mappingfile_path, dtype=str, header=None)
        if mapping_table.isnull().values.any():
            print("The custom mapping file contains empty cells!")
            sys.exit(1)

        pseudo_mapping = {row[0]: row[1] for row in mapping_table.to_numpy(dtype=str)}

        # Convert the custom pseudo mapping to json format.
        json_pseudo_response = json.dumps(pseudo_mapping, indent=4)

        # Generate random day shifts between -30 and 30 days for all pseudonyms
        # if specified. Otherwise, set day shifts to 0.
        day_shifts = {
            p: np.random.randint(-30, 31) if args.shift_days else 0
            for p in pseudo_mapping.keys()
        }
        json_day_shift_response = json.dumps(day_shifts, indent=4)

    # Print the old / new pseudonyms and day shifts if verbose mode is on.
    if args.verbose:
        print(f"Old / new pseudonyms: {json_pseudo_response} \n")
        print(f"Day shifts: {json_day_shift_response}")

    # Save the old /new pseudonyms mapping to a json file.
    json_pseudo_response_path = os.path.normpath(
        os.path.join(output_dir, f"new_ids_{args.project_name}.json")
    )
    with open(json_pseudo_response_path, "w") as f:
        f.write(json_pseudo_response)

    # Save the day shifts to a json file.
    json_day_shift_response_path = os.path.normpath(
        os.path.join(output_dir, f"day_shift_{args.project_name}.json")
    )
    with open(json_day_shift_response_path, "w") as f:
        f.write(json_day_shift_response)

    print("Done!")


if __name__ == "__main__":
    main()
