# Copyright 2018-2026 Lausanne University Hospital and University of Lausanne,
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

"""Docker wrapper scripts for PACSIFIER CLI commands.

These scripts provide a convenient way to run PACSIFIER CLI commands via Docker
without needing to remember the full docker run command syntax.
"""

import argparse
import os
import subprocess
import sys

from pacsifier.info import DOCKER_REGISTRY


def get_docker_image_name():
    """Get the Docker image name for PACSIFIER.

    Returns:
        str: The Docker image name, defaulting to the Quay.io registry image
    """
    return os.environ.get('PACSIFIER_DOCKER_IMAGE', f'{DOCKER_REGISTRY}:latest')


def get_docker_user_args():
    """Get the Docker arguments selecting the user the container runs as.

    The image runs as a non-root user by default. To let it write to bind-mounted
    host directories, the container is run with the UID:GID of the current user.
    This can be overridden with the ``PACSIFIER_DOCKER_USER`` environment variable
    (e.g. ``1000:1000``); an empty value keeps the image's default user.

    Returns:
        list: The ``--user`` arguments, or an empty list if none should be used
    """
    if 'PACSIFIER_DOCKER_USER' in os.environ:
        user = os.environ['PACSIFIER_DOCKER_USER'].strip()
        return ['--user', user] if user else []
    if hasattr(os, 'getuid') and hasattr(os, 'getgid'):
        return ['--user', f'{os.getuid()}:{os.getgid()}']
    return []


def run_docker_command(command_args, additional_volumes=None, additional_args=None):
    """Run a PACSIFIER command via Docker.

    Args:
        command_args (list): The command and arguments to run inside the container
        additional_volumes (list): Additional volume mounts (optional)
        additional_args (list): Additional Docker arguments (optional)
    """
    docker_image = get_docker_image_name()

    # Base Docker command
    # -i: Keep STDIN open even if not attached (helps with output visibility)
    # -t: Allocate a pseudo-TTY so tools stream output in real time (only when a TTY is available)
    # -e PYTHONUNBUFFERED=1: Disable Python output buffering for real-time terminal output
    docker_cmd = [
        'docker', 'run', '--rm', '--net=host', '-i',
        '-e', 'PYTHONUNBUFFERED=1'
    ]

    # Only allocate a pseudo-TTY when running in an interactive terminal
    if sys.stdout.isatty():
        docker_cmd.insert(docker_cmd.index('-i') + 1, '-t')

    # Run as the host user so files written to bind mounts are owned by that user
    docker_cmd.extend(get_docker_user_args())

    # Add additional Docker arguments if provided
    if additional_args:
        docker_cmd.extend(additional_args)

    # Add volume mounts
    volumes = additional_volumes or []
    for volume in volumes:
        docker_cmd.extend(['-v', volume])

    # Add the image and command
    docker_cmd.append(docker_image)
    docker_cmd.extend(command_args)

    # Run the command
    # Pass stdout and stderr through to ensure real-time output visibility
    try:
        subprocess.run(docker_cmd, check=True, stdout=None, stderr=None)
    except subprocess.CalledProcessError as e:
        print(f"Error running Docker command: {e}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: Docker not found. Please ensure Docker is installed and in your PATH.",
              file=sys.stderr)
        sys.exit(1)


def docker_pacsifier():
    """Docker wrapper for the main pacsifier command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_pacsifier -c config.json -i -s -q query.csv -d /output
        docker_pacsifier --config /path/to/config.json --info --save \\
            --queryfile /path/to/query.csv --out_directory /output
        docker_pacsifier -c config.json --move -q query.csv
    """
    )

    # Mirror the arguments of the real pacsifier CLI
    parser.add_argument('-c', '--config', required=True, help='Path to configuration file')
    parser.add_argument('-s', '--save', action='store_true',
                        help="Store images resulting from query (cannot be used with '--move')")
    parser.add_argument('-i', '--info', action='store_true',
                        help='Store parsed version of findscu output (DICOM header subset)')
    parser.add_argument('-m', '--move', action='store_true',
                        help="Move images resulting from query (cannot be used with '--save')")
    parser.add_argument('-q', '--queryfile',
                        help="Path to query file (mandatory if '--save' or '--move' is used)")
    parser.add_argument('-d', '--out_directory',
                        help='Output directory where images will be saved')
    parser.add_argument('-u', '--upload', action='store_true',
                        help='Upload DICOM images to PACS server')
    parser.add_argument('--upload_directory', '-ud',
                        help="Directory containing DICOM images to upload "
                        "(only used with '--upload')")
    parser.add_argument('--resume', action='store_true',
                        help='Resume extraction by skipping already downloaded series')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose progress information during retrieval')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    # Set Docker image if provided
    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    # Build command arguments
    command_args = ['pacsifier']

    # Add required config file
    command_args.extend(['-c', '/config.json'])

    # Add optional arguments
    if args.save:
        command_args.append('--save')
    if args.info:
        command_args.append('-i')
    if args.move:
        command_args.append('--move')
    if args.queryfile:
        command_args.extend(['-q', '/query.csv'])
    if args.out_directory:
        command_args.extend(['-d', '/output'])
    if args.upload:
        command_args.append('--upload')
    if args.upload_directory:
        command_args.extend(['--upload_directory', '/upload'])
    if args.resume:
        command_args.append('--resume')
    if args.verbose:
        command_args.append('--verbose')

    # Add any unknown arguments
    command_args.extend(unknown_args)

    # Build volume mounts
    volumes = []
    if args.config:
        volumes.append(f"{os.path.abspath(args.config)}:/config.json")
    if args.queryfile:
        volumes.append(f"{os.path.abspath(args.queryfile)}:/query.csv")
    if args.out_directory:
        volumes.append(f"{os.path.abspath(args.out_directory)}:/output")
    if args.upload_directory:
        volumes.append(f"{os.path.abspath(args.upload_directory)}:/upload")

    run_docker_command(command_args, additional_volumes=volumes)


def docker_get_pseudonyms():
    """Docker wrapper for the get_pseudonyms command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-get-pseudonyms via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_get_pseudonyms --mode de-id -c config.json -q query.csv -a ProjectName -d /output
        docker_get_pseudonyms --mode custom -mf mapping.csv -a ProjectName -d /output --shift-days
    """
    )

    parser.add_argument('--mode', '-m', choices=['de-id', 'custom'],
                        default='de-id', help='Mode of operation: de-id or custom')
    parser.add_argument('--config', '-c',
                        help='Deidentification configuration file path '
                        '(required for --mode de-id)')
    parser.add_argument('--queryfile', '-q',
                        help='Path to PACSIFIER query file '
                        '(required for --mode de-id)')
    parser.add_argument('--mappingfile', '-mf',
                        help='Path to custom mapping file in CSV format '
                        '(required for --mode custom)')
    parser.add_argument('--shift-days', action='store_true',
                        help='Generate random day shifts for all pseudonyms '
                        'in the +- 30 days range')
    parser.add_argument('--project_name', '-a', required=True,
                        help='Name of the project in GPCR '
                        '(may or may not correspond to Kheops album)')
    parser.add_argument('--out_directory', '-d', required=True,
                        help='Output directory where the pseudonyms will be saved as a json')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print verbose output')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    # Build command arguments
    command_args = ['pacsifier-get-pseudonyms']

    if args.mode:
        command_args.extend(['--mode', args.mode])

    volumes = []

    if args.mode == 'de-id':
        if not args.config or not args.queryfile:
            parser.error("--config and --queryfile are required for --mode de-id")
        command_args.extend(['--config', '/config.json'])
        command_args.extend(['--queryfile', '/query.csv'])
        volumes.append(f"{os.path.abspath(args.config)}:/config.json")
        volumes.append(f"{os.path.abspath(args.queryfile)}:/query.csv")
    elif args.mode == 'custom':
        if not args.mappingfile:
            parser.error("--mappingfile is required for --mode custom")
        command_args.extend(['--mappingfile', '/mapping.csv'])
        volumes.append(f"{os.path.abspath(args.mappingfile)}:/mapping.csv")

    if args.shift_days:
        command_args.append('--shift-days')

    command_args.extend(['--project_name', args.project_name])
    command_args.extend(['--out_directory', '/output'])

    if args.verbose:
        command_args.append('--verbose')

    volumes.append(f"{os.path.abspath(args.out_directory)}:/output")
    command_args.extend(unknown_args)

    run_docker_command(command_args, additional_volumes=volumes)


def docker_add_karnak_tags():
    """Docker wrapper for the add_karnak_tags command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-add-karnak-tags via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_add_karnak_tags -d /input -n new_ids.json -a AlbumName
        docker_add_karnak_tags --in_folder /path/to/input --new_ids /path/to/new_ids.json
            --album_name AlbumName --day_shift /path/to/day_shift.json
    """
    )

    parser.add_argument('--in_folder', '-d', required=True,
                        help='Directory to the dicom files')
    parser.add_argument('--new_ids', '-n', required=True,
                        help='List of new patient IDentifiers (JSON file)')
    parser.add_argument('--day_shift', '-s', help='List of day shift per patient (JSON file)')
    parser.add_argument('--album_name', '-a', required=True,
                        help='Name of destination Kheops album to route the tagged study')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    command_args = ['pacsifier-add-karnak-tags', '--in_folder', '/input',
                    '--new_ids', '/new_ids.json']

    volumes = [
        f"{os.path.abspath(args.in_folder)}:/input",
        f"{os.path.abspath(args.new_ids)}:/new_ids.json"
    ]

    if args.day_shift:
        command_args.extend(['--day_shift', '/day_shift.json'])
        volumes.append(f"{os.path.abspath(args.day_shift)}:/day_shift.json")

    command_args.extend(['--album_name', args.album_name])
    command_args.extend(unknown_args)

    run_docker_command(command_args, additional_volumes=volumes)


def docker_anonymize_dicoms():
    """Docker wrapper for the anonymize_dicoms command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-anonymize via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_anonymize_dicoms -d /input -o /output
        docker_anonymize_dicoms --in_folder /path/to/input --out_folder /path/to/output
            --new_ids /path/to/new_ids.json
        docker_anonymize_dicoms -d /input -o /output -i -p -a
        """
    )

    parser.add_argument('--in_folder', '-d', required=True,
                        help='Directory to the dicom files to be anonymized')
    parser.add_argument('--out_folder', '-o', required=True,
                        help='Output directory where the anonymized dicoms will be saved')
    parser.add_argument('--delete_identifiable', '-i', action='store_true',
                        help='Delete identifiable files like Dose reports')
    parser.add_argument('--remove_private_tags', '-p', action='store_true',
                        help='Remove private tags')
    parser.add_argument('--fuzz_acq_dates', '-a', action='store_true',
                        help='Fuzz acquisition dates')
    parser.add_argument('--new_ids', '-n', help='List of new ids (JSON file)')
    parser.add_argument('--keep_patient_dir_names', '-k', action='store_true',
                        help='Do not rename patient directories, keep original IDs')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    command_args = ['pacsifier-anonymize', '--in_folder', '/input',
                    '--out_folder', '/output']

    volumes = [
        f"{os.path.abspath(args.in_folder)}:/input",
        f"{os.path.abspath(args.out_folder)}:/output"
    ]

    if args.delete_identifiable:
        command_args.append('--delete_identifiable')
    if args.remove_private_tags:
        command_args.append('--remove_private_tags')
    if args.fuzz_acq_dates:
        command_args.append('--fuzz_acq_dates')
    if args.new_ids:
        command_args.extend(['--new_ids', '/new_ids.json'])
        volumes.append(f"{os.path.abspath(args.new_ids)}:/new_ids.json")
    if args.keep_patient_dir_names:
        command_args.append('--keep_patient_dir_names')

    command_args.extend(unknown_args)

    run_docker_command(command_args, additional_volumes=volumes)


def docker_extract_carestream_report():
    """Docker wrapper for the extract_carestream_report command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-extract-carestream-report via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_extract_carestream_report -d data_folder
        docker_extract_carestream_report --data_folder /path/to/data
    """
    )

    parser.add_argument('-d', '--data_folder', required=True, help='Path to data folder')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    command_args = ['pacsifier-extract-carestream-report', '-d', '/data']
    command_args.extend(unknown_args)

    volumes = [
        f"{os.path.abspath(args.data_folder)}:/data"
    ]

    run_docker_command(command_args, additional_volumes=volumes)


def docker_move_dumps():
    """Docker wrapper for the move_dumps command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-move-csv via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_move_dumps -d dicom_path -o info_folder
        docker_move_dumps --data_folder /path/to/dicom --info_folder /path/to/info
    """
    )

    parser.add_argument('-d', '--data_folder', required=True, help='Path to dicom folder')
    parser.add_argument('-o', '--info_folder', required=True, help='Path to info folder')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    command_args = ['pacsifier-move-csv', '-d', '/dicom', '-o', '/info']
    command_args.extend(unknown_args)

    volumes = [
        f"{os.path.abspath(args.data_folder)}:/dicom",
        f"{os.path.abspath(args.info_folder)}:/info"
    ]

    run_docker_command(command_args, additional_volumes=volumes)


def docker_create_dicomdir():
    """Docker wrapper for the create_dicomdir command."""
    parser = argparse.ArgumentParser(
        description="Run pacsifier-create-dicomdir via Docker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
        docker_create_dicomdir -d /input -o /output
        docker_create_dicomdir --in_folder /path/to/input --out_folder /path/to/output
    """
    )

    parser.add_argument('--in_folder', '-d', default='./data',
                        help='Directory to the dicom files')
    parser.add_argument('--out_folder', '-o', default='./data',
                        help='Output directory where the dicoms and DICOMDIR will be saved')
    parser.add_argument('--image',
                        help='Docker image name (overrides PACSIFIER_DOCKER_IMAGE env var)')

    args, unknown_args = parser.parse_known_args()

    if args.image:
        os.environ['PACSIFIER_DOCKER_IMAGE'] = args.image

    command_args = ['pacsifier-create-dicomdir', '--in_folder', '/input',
                    '--out_folder', '/output']
    command_args.extend(unknown_args)

    volumes = [
        f"{os.path.abspath(args.in_folder)}:/input",
        f"{os.path.abspath(args.out_folder)}:/output"
    ]

    run_docker_command(command_args, additional_volumes=volumes)


if __name__ == "__main__":
    print("This module contains Docker wrapper functions for PACSIFIER CLI commands.")
    print("Use the individual wrapper scripts (docker_pacsifier, docker_get_pseudonyms, etc.)")
    sys.exit(1)
