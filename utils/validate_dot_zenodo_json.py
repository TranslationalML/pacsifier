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

"""This script validates the `.zenodo.json` present in the top-level of the repository.

It uses the json schema from https://github.com/zenodraft/metadata-schema-zenodo.

It is used in the CI/CD pipeline to validate the `.zenodo.json` file to make sure
it is compliant with the Zenodo metadata schema before we make a new release.

"""

import os
import sys
import argparse
import json
import urllib.request
import jsonschema


def get_parser() -> argparse.ArgumentParser:
    """Get parser object."""
    parser = argparse.ArgumentParser(
        description="Validate a `.zenodo.json` file specified by the input argument."
    )
    parser.add_argument(
        "--zenodo-json",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "..", ".zenodo.json"),
        help="Path to the `.zenodo.json` file to validate.",
    )
    parser.add_argument(
        "--zenodo-schema",
        type=str,
        default="https://raw.githubusercontent.com/zenodraft/metadata-schema-zenodo/main/schema.json",
        help="URL or path to the json schema to use for validation.",
    )
    return parser


def main():
    """Main function."""
    # Parse the input arguments
    parser = get_parser()
    args = parser.parse_args()

    if args.zenodo_schema.startswith("http"):
        # Download the json schema from Zenodo
        print(f'Downloading the json schema ({args.zenodo_schema})...')
        with urllib.request.urlopen(args.zenodo_schema) as f:
            schema = json.loads(f.read().decode())
    else:
        # Check if the file exists
        if not os.path.isfile(args.zenodo_schema):
            print(
                "The json schema file does not exist at the specified path."
            )
            sys.exit(1)
        # Load the json schema from the specified path
        print(f'Loading the json schema ({args.zenodo_schema})...')
        with open(args.zenodo_schema, "r") as f:
            try:
                schema = json.load(f)
            except json.JSONDecodeError:
                print(
                    "The json schema file does not contain valid json."
                )
                sys.exit(1)

    # Check if the .zenodo.json file exists
    if not os.path.isfile(args.zenodo_json):
        print("The .zenodo.json file does not exist at the specified path.")
        sys.exit(1)

    # Load the .zenodo.json file
    with open(args.zenodo_json, "r") as f:
        try:
            print(f'Loading the .zenodo.json file ({args.zenodo_json})...')
            zenodo_json = json.load(f)
        except json.JSONDecodeError:
            print("The .zenodo.json file does not contain valid json.")
            sys.exit(1)

    # Validate the .zenodo.json file
    print(f'Validating...\n')
    print(json.dumps(zenodo_json, indent=2))
    print('\n')
    try:
        jsonschema.validate(zenodo_json, schema)
    except jsonschema.exceptions.ValidationError as e:
        print(f'Validation failed:\n\n{e}')
        sys.exit(1)
    print('Congrats! Validation of the .zenodo.json file successful!')
    

if __name__ == "__main__":
    main()
