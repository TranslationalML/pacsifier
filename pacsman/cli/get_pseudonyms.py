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

"""Script to get the new pseudonyms and day shifts for a list of PatientIDs in a PACSMAN query file."""

import ast
import sys, os, argparse
import json, csv, requests
from typing import Dict, Any
from pandas import read_csv
from pacsman.cli.pacsman import check_query_table_allowed_filters


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
    """Convert PACSMAN query to json format the de-ID API can understand.

    Args:
        queryfile: the filename of the PACSMAN query file
        project_name: the name of the project in GPCR (may or may not correspond to Kheops album)

    Returns:
        JSON object suitable for the API

    """
    json_new_str = '{"project": "' + project_name + '", "PatientIDList": ['
    patient_list_str = ""

    with open(queryfile, newline="") as csvfile:
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
                "deid_URL": "https://deid.gpcr-project.org",
                "deid_token": "1234567890"
            }
        
        query_json: the PACSMAN query formatted as a dictionary

    Returns:
        JSON object containing the new pseudonyms for each patient

    """
    head = {"Authorization": f'token {deid_parameters["deid_token"]}'}

    response = requests.post(
        deid_parameters["deid_URL"], headers=head, json=query_json, verify=False
    )

    resp = ast.literal_eval(response.text)
    json_resp = json.dumps(resp)

    return json_resp


def get_deid_day_shifts(deid_parameters: dict, query_json: dict) -> None:
    """Run the de-ID request for day shifts and return the response as a json.

    Args:
        deid_parameters: dictionary containing the de-ID URL and token in the following format::
            
            {
                "deid_URL": "https://deid.gpcr-project.org",
                "deid_token": "1234567890"
            }
        
        query_json: the PACSMAN query formatted as a dictionary

    Returns:
        JSON object containing the day shifts for each patient

    """
    head = {"Authorization": f'token {deid_parameters["deid_token"]}'}

    response = requests.post(
        deid_parameters["deid_URL"] + "_shift", headers=head, json=query_json, verify=False
    )

    resp = ast.literal_eval(response.text)
    json_resp = json.dumps(resp)
    
    return json_resp


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
        help="Path to PACSMAN query file (used to find PatientIDs, required for --mode de-id)",
        required="--mode de-id" in sys.argv,
    )
    parser.add_argument(
        "--mappingfile",
        "-mf",
        help="Path to custom mapping file in CSV format (required for --mode custom)",
        required="--mode custom" in sys.argv,
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

    return parser


def main():
    """Main function of the script."""
    # Create parser object and parse command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # Check the case where the queryfile, config, or project_name is missing.
    # If it is the case print help.
    # TODO: Can be directly done with argparse with the required=True option.
    if args.queryfile is None or args.config is None or args.project_name is None:
        print("Missing mandatory parameter --queryfile or --config or --project_name!")
        parser.print_help()
        sys.exit()

    # Check if the config file exists.
    config_path = os.path.abspath(args.config)
    if not os.path.isfile(config_path):
        print(f"Config file {config_path} does not exist!")
        sys.exit()
    
    # Check if the output directory exists. If not, create it.
    output_dir = os.path.abspath(args.out_directory)
    if not os.path.isdir(output_dir):
        print(f"Output directory {output_dir} does not exist! Creating...")
        os.makedirs(output_dir, exist_ok=True)

    # Check if the queryfile exists.
    query_file = os.path.abspath(args.queryfile)
    if not os.path.isfile(query_file):
        print(f"Query file {query_file} does not exist!")
        sys.exit()

    # Read and validate the queryfile.
    table = read_csv(args.queryfile, dtype=str).fillna("")
    check_query_table_allowed_filters(table)

    # Reading config file for deid parameters.
    with open(config_path) as f:
        deid_parameters = json.load(f)
        check_config_file_deid(deid_parameters)
    
    # TODO should enable reading IDs from json file too, or scan from disk.

    # Convert the queryfile to json format.
    query_json = convert_csv_to_deid_json(query_file, args.project_name)

    # Get the new pseudonyms
    json_response = get_deid_pseudonyms(deid_parameters, query_json)
    print(json_response)

    with open(
        os.path.normpath(
            os.path.join(output_dir, f"new_ids_{args.project_name}.json")
        ),
        "w",
    ) as f:
        f.write(json_response)

    # Get day shift
    json_response = get_deid_day_shifts(deid_parameters, query_json)

    with open(
        os.path.normpath(
            os.path.join(output_dir, f"day_shift_{args.project_name}.json")
        ),
        "w",
    ) as f:
        f.write(json_response)

    print("Done!")


if __name__ == "__main__":
    main()
