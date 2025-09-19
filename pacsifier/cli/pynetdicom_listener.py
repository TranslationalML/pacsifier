#!/usr/bin/env python3
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

"""Simple pynetdicom Storage SCP listener to receive DICOM files from Karnak."""

import argparse
from pacsifier.core.pynetdicom_listener import start_listener


def main():
    """Main function to start the pynetdicom listener."""
    parser = argparse.ArgumentParser(
        description="Simple pynetdicom Storage SCP listener to receive DICOM files from Karnak"
    )
    
    parser.add_argument(
        "--address",
        "-a",
        required=True,
        help="Address to listen on"
    )
    
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        required=True,
        help="Port to listen on"
    )
    
    parser.add_argument(
        "--aet",
        required=True,
        help="Application Entity Title"
    )
    
    parser.add_argument(
        "--output-dir",
        "-o",
        required=True,
        help="Directory to save received DICOM files"
    )
    
    args = parser.parse_args()
    
    # Start the listener using the shared module
    start_listener(args.address, args.port, args.aet, args.output_dir)


if __name__ == "__main__":
    main()
