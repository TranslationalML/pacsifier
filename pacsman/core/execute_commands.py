# Imports .
from datetime import date
import os
import warnings
import shlex
import subprocess
import platform

from pacsman.core.sanity_checks import (
    check_parameters_inputs,
    check_ids,
    check_server_address,
    check_port,
    check_AET,
    check_query_retrieval_level,
)

warnings.filterwarnings("ignore")

# Query default parameters
PATIENT_ID = '"PAT004"'
STUDY_INSTANCE_UID, SERIES_INSTANCE_UID, OUTPUT_DIR = (
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.461"',
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.462"',
    ".",
)

PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"

# Query squeletons.
ECHO_COMMAND = (
    'echoscu -ll trace -aec "{server_aet}" -aet "{aet}" {server_address} {port}'
)
FIND_COMMAND = (
    "findscu -v {modified_params} --study "
    "-k QueryRetrieveLevel={query_retrieval_level} -k 0010,0020={patient_id} "
    "-k 20,11 -k 10,10 -k 10,1010 -k 0020,000d={study_uid} --key 0020,000e={series_instance_uid} "
    "--key 0008,103E={series_description} --key 18,1030={protocol_name} --key 8,22={acquisition_date} "
    "--key 0008,0020={study_date} --key 0010,0010={patient_name} --key 10,30={patient_birthdate} "
    "--key 8,30 --key 18,1000={device_serial_number} --key 8,60={modality} --key 8,8={image_type} "
    "--key 8,1030={study_description} --key 8,50={accession_number} --key 18,24={sequence_name}"
)
MOVE_COMMAND = (
    'movescu -ll debug {modified_params} -aem "{aet}" -k 0008,0052="PATIENT" --patient '
    "--key 0010,0020={patient_id} --key 0020,000d={study_instance_uid} "
    "--key 0020,000e={series_instance_uid} --key 0008,0020={study_date} "
    "--port {move_port} -od {output_dir}"
)
MOVE_REMOTE_COMMAND = (
    'movescu -ll debug {modified_params} -aem "{move_aet}" -k 0008,0052="PATIENT" --patient '
    "--key 0010,0020={patient_id} --key 0020,000d={study_instance_uid} "
    "--key 0020,000e={series_instance_uid} --key 0008,0020={study_date}"
)


########################################################################################################################
########################################################FUNCTIONS#######################################################
########################################################################################################################


def echo(
    server_address: str = "www.dicomserver.co.uk",
    port: int = 104,
    server_aet: str = "theServertAET",
    aet: str = "AET",
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
) -> str:
    """Checks that the PACS server can be reached and accepts associations.

    Args:
        server_address: PACS server IP address.
        port: PACS server port for incoming requests. Default is 104.
        server_aet: PACS server AET. Default is "theServerAET".
        aet: AET of the calling entity. Default is "AET".
        log_dir: Folder for the logs where the log file (log.txt) and
                    the fails file (fails.txt) produced by run() will be written.
                    Default is "./logs" e.g. the logs/ folder in the current working directory.

    Returns:
        string: The log lines.

    """
    check_server_address(server_address)
    check_port(port)
    check_AET(server_aet, server=True)
    check_AET(aet)

    command = ECHO_COMMAND.format(
        server_aet=server_aet, aet=aet, server_address=server_address, port=port
    )

    return run(
        query=command,
        log_dir=log_dir,
    )


def find(
    aet: str,
    server_address: str = "www.dicomserver.co.uk",
    server_aet: str = "theServerAET",
    port: int = 104,
    query_retrieval_level: str = "SERIES",
    patient_id: str = "",
    study_uid: str = "",
    series_instance_uid: str = "",
    series_description: str = "",
    protocol_name: str = "",
    acquisition_date: str = "",
    patient_name: str = "",
    patient_birthdate: str = "",
    study_date: str = "",
    device_serial_number: str = "",
    modality: str = "",
    image_type: str = "",
    study_description: str = "",
    accession_number: str = "",
    sequence_name: str = "",
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
) -> str:
    """Builds a query for findscu of QueryRetrieveLevel of series using the parameters passed as arguments.

    Args:
        aet: called AET.
        server_address: PACS server IP address. Default is "www.dicomserver.co.uk".
        server_aet: PACS server AET. Default is "theServerAET".
        port: PACS server port for incoming requests. Default is 104.
        query_retrieval_level: query retrieval level which can only take values in
                           {SERIES, STRUDY, PATIENT, IMAGE}. Default is "SERIES".
        patient_id: patient id. Default is "".
        study_uid: study unique identifier. Default is "".
        series_instance_uid: series Instance UID. Default is "".
        series_description: series Description. Default is "".
        protocol_name: protocol name. Default is "".
        acquisition_date: acquisition date. Default is "".
        patient_name: patient's name. Default is "".
        patient_birthdate: patient's birth date. Default is "".
        study_date: study Date. Default is "".
        device_serial_number: MRI device serial number. Default is "".
        modality: modality. Default is "".
        image_type: image type. Default is "".
        study_description: description of the study. Default is "".
        accession_number: accession number. Default is "".
        sequence_name: sequence name. Default is "".
        log_dir: Folder for the logs where the log file (log.txt) and
                 the fails file (fails.txt) produced by run() will be written.
                 Default is "./logs" e.g. the logs/ folder in the current working directory.

    Returns:
        string: The log lines.

    """

    check_ids(patient_id)
    check_ids(study_uid, attribute="Study instance UID")
    check_ids(series_instance_uid, attribute="Series instance UID")
    check_port(port)
    check_query_retrieval_level(query_retrieval_level)

    modified_params = replace_default_params(
        PARAMETERS, aet, server_address, server_aet, port
    )
    command = FIND_COMMAND.format(
        modified_params=modified_params,
        query_retrieval_level=query_retrieval_level,
        patient_id=patient_id,
        study_uid=study_uid,
        series_instance_uid=series_instance_uid,
        series_description=series_description,
        protocol_name=protocol_name,
        acquisition_date=acquisition_date,
        study_date=study_date,
        patient_name=patient_name,
        patient_birthdate=patient_birthdate,
        device_serial_number=device_serial_number,
        modality=modality,
        image_type=image_type,
        study_description=study_description,
        accession_number=accession_number,
        sequence_name=sequence_name,
    )

    return run(
        query=command,
        log_dir=log_dir,
    )


def get(
    aet: str,
    study_date: str,
    server_address: str = "www.dicomserver.co.uk",
    server_aet: str = "theServerAET",
    port: int = 104,
    patient_id: str = PATIENT_ID,
    study_instance_uid: str = STUDY_INSTANCE_UID,
    series_instance_uid: str = SERIES_INSTANCE_UID,
    move_port: int = 4006,
    output_dir: str = OUTPUT_DIR,
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
) -> str:
    """Builds a query for movescu.

    Args:
        aet: called AET.
        study_date: study date.
        server_address: PACS server IP address. Default is "www.dicomserver.co.uk".
        server_aet: PACS server AET. Default is "theServerAET".
        port: PACS server port for incoming requests. Default is 104.
        patient_id: patient id. Default is pacsman.core.execute_commands.patient_id.
        study_instance_uid: study instance unique idetifier. Default is
                          pacsman.core.execute_commands.study_instance_uid.
        series_instance_uid: series instance unique identifier. Default is
                           pacsman.core.execute_commands.series_instance_uid.
        move_port: port used for movescu command. Default is 4006.
        output_dir: directory of output files. Default is "." e.g. the current working directory.
        log_dir: Folder for the logs where the log file (log.txt) and
                 the fails file (fails.txt) produced by run() will be written.
                 Default is "./logs" e.g. the logs/ folder in the current working directory.

    Returns:
        string: The log lines.

    """
    check_ids(patient_id)
    check_ids(series_instance_uid, attribute="Series instance UID")
    check_ids(study_instance_uid, attribute="Study instance UID")
    check_port(move_port)
    check_port(port)

    modified_params = replace_default_params(
        PARAMETERS, aet, server_address, server_aet, port
    )
    command = MOVE_COMMAND.format(
        modified_params=modified_params,
        aet=aet,
        patient_id=patient_id,
        study_instance_uid=study_instance_uid,
        series_instance_uid=series_instance_uid,
        study_date=study_date,
        move_port=move_port,
        output_dir=output_dir,
    )
    return run(
        query=command,
        log_dir=log_dir,
    )


def move_remote(
    aet: str,
    study_date: str,
    server_address: str = "www.dicomserver.co.uk",
    server_aet: str = "theServerAET",
    port: int = 104,
    patient_id: str = PATIENT_ID,
    study_instance_uid: str = STUDY_INSTANCE_UID,
    series_instance_uid: str = SERIES_INSTANCE_UID,
    move_aet: str = "theMoveAET",
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
) -> str:
    """Builds a query for movescu.

    Args:
        aet: called AET.
        study_date: study date.
        server_address: PACS server IP address. Default is "www.dicomserver.co.uk".
        server_aet: PACS server AET. Default is "theServerAET".
        port: PACS server port for incoming requests. Default is 104.
        patient_id: patient id. Default is pacsman.core.execute_commands.patient_id.
        study_instance_uid: study instance unique idetifier. Default is
                          pacsman.core.execute_commands.study_instance_uid.
        series_instance_uid: series instance unique identifier. Default is
                           pacsman.core.execute_commands.series_instance_uid.
        move_aet: AET where to move the images. Default is "theMoveAET".
        log_dir: Folder for the logs where the log file (log.txt) and
                 the fails file (fails.txt) produced by run() will be written.
                 Default is "./logs" e.g. the logs/ folder in the current working directory.

    Returns:
        string: The log lines.

    """
    check_ids(patient_id)
    check_ids(series_instance_uid, attribute="Series instance UID")
    check_ids(study_instance_uid, attribute="Study instance UID")
    check_port(port)
    check_AET(move_aet)

    modified_params = replace_default_params(
        PARAMETERS, aet, server_address, server_aet, port
    )
    command = MOVE_REMOTE_COMMAND.format(
        modified_params,
        move_aet,
        patient_id,
        study_instance_uid,
        series_instance_uid,
        study_date,
    )

    return run(
        query=command,
        log_dir=log_dir,
    )


def write_file(results: str, file: str = "output.txt") -> None:
    """Writes results in file passed in parameters using the parameters passed as arguments.

    Args:
        results: a str of lines of logs
        file: path to text file where the log lines in results will be written

    """

    file = os.path.abspath(file)

    # Create containing directories if they do not exist
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file), exist_ok=True)

    if not os.path.exists(file):
        # os.mknod(file) # not cross-platform - unsupported on os X without root
        f = open(file, "w", encoding="utf_8")
    else:
        f = open(file, "a", encoding="utf_8")
    for line in results:
        f.write(str(line) + "\n")
    f.close()


def replace_default_params(
    parameters: str, AET: str, server_address: str, server_aet: str, port: int
) -> str:
    """Helper function to replace default parameters in queries by new parameters.

    Args:
        parameters: The string containing default parameters for dicomserver
        AET: Called AET
        server_address: PACS server IP address
        server_aet: PACS server AET
        port: PACS server port for incoming requests
    Returns:
        string: modified parameters with input values.

    """
    check_parameters_inputs(AET, server_address, server_aet, port)

    return (
        parameters.replace("theServerAET", server_aet)
        .replace(" 104", " " + str(port))
        .replace("88.202.185.144", server_address)
        .replace("MY_AET", AET)
    )


def run(query: str, log_dir: str = ".") -> str:
    """Runs the command passed as parameter.

    Args:
        query: Query command line to be executed.
        log_dir: Directory where the log file (log.txt) and
                 the fails file (fails.txt) will be written.
                 Default is "." e.g. the current working directory.

    Returns:
        string: The log lines.

    """
    # Create output directory if it does not exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    try:
        # The replace in the line below is necessary for the windows deployment.
        cmd = shlex.split(query.replace("\\", "\\\\"))
        with open(os.path.join(log_dir, "log.txt"), "a") as f:
            f.write(query + "\n")
    except ValueError as e:
        print("* Command parsing error: {}".format(" ".join(cmd)))
        exit()

    try:
        if "Windows" in platform.platform():
            completed = subprocess.check_output(cmd, stderr=subprocess.PIPE)
            lines = completed.decode("latin1").splitlines()
        else:
            completed = subprocess.run(
                cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True
            )
            lines = completed.stderr.decode("latin1").splitlines()
        lines = [line.replace("\x00", "") for line in lines]
    except subprocess.CalledProcessError as e:
        print(
            "* Command did not succeed: {}, return code {}".format(
                " ".join(cmd), e.returncode
            )
        )
        print("* Output: {}".format(e.stderr))

        with open(os.path.join(log_dir, "fails.txt"), "a") as f:
            f.write(query + "\n")

        print(e.returncode)
        print(e.output)
        lines = ""

    return lines
