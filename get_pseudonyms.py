import sys, os, argparse
import json, csv, requests
from typing import Dict, Any
from pandas import read_csv
from pacsman import check_query_table_allowed_filters

def check_config_file_deid(config_file: Dict[str, str]) -> None:
    """
    Checks that the config file passed as a parameter is valid.
    Args:
        config_file : dictionary loaded from the config json file.
    """
    items = set(config_file.keys())
    valid_keys = ["deid_URL", "deid_token"]
    if items != set(valid_keys):
        raise ValueError("Invalid config file! Must contain these and only these keys: " + ' '.join(valid_keys))


def convert_csv_to_json(queryfile: str, project_name: str) -> Any:
    """
    Convert PACSMAN query to json format the de-ID API can understand
    Args:
        queryfile: the filename of the PACSMAN query file
        project_name: the name of the project in GPCR (may or may not correspond to Kheops album)
    Returns:
        JSON object suitable for the API
    """
    json_new_str = '{"project": "' + project_name + '", "PatientIDList": ['
    patient_list_str = ""

    with open(queryfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['PatientID'] != '':
                patient_list_str = patient_list_str + '{"PatientID": "' + row['PatientID'] + '"}, '

    if len(patient_list_str) > 0:
        if patient_list_str.endswith(', '):
            patient_list_str = patient_list_str[:-2]
        json_new_str = json_new_str + patient_list_str + "]}"
    else:
        json_new_str = "{}"

    return json.loads(json_new_str)


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', "-c", help='Deidentification configuration file path',
                        default=os.path.join(".", "files", "config_deid.json"))
    parser.add_argument("--queryfile", "-q", help='Path to PACSMAN query file (used to find PatientIDs)')
    parser.add_argument("--project_name", "-a", help='Name of the project in GPCR (may or may not correspond to Kheops album)')
    parser.add_argument("--out_directory", "-d", help='Output directory where the pseudonyms will be saved as a json',
                        default=os.path.join(".", "data"))

    args = parser.parse_args()

    config_path = args.config
    # Reading config file.
    with open(config_path) as f:
        parameters = json.load(f)
        check_config_file_deid(parameters)

    output_dir = args.out_directory

    #TODO should enable reading IDs from json file too, or scan from disk.

    # Check the case where the queryfile, config, or project_name is missing. If it is the case print help.
    if args.queryfile is None or args.config is None or args.project_name is None:
        print("Missing mandatory parameter --queryfile or --config or --project_name!")
        parser.print_help()
        sys.exit()

    # Read and validate the queryfile.
    table = read_csv(args.queryfile, dtype=str).fillna("")
    check_query_table_allowed_filters(table)

    # build POST request
    head = {'Authorization': 'token {}'.format(parameters['deid_token'])}

    json_data = convert_csv_to_json(args.queryfile, args.project_name)
    response = requests.post(parameters['deid_URL'], headers=head, json=json_data, verify=False)

    print(response.text)
    with open(os.path.normpath(os.path.join(args.out_directory, "new_ids_{}.json".format(args.project_name))), "w") as f:
        f.write(response.text)


if __name__ == "__main__":
    main(sys.argv[1:])
