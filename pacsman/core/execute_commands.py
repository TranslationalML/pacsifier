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
PATIENTID = '"PAT004"'
STUDYINSTANCEUID, SERIESINSTANCEUID, OUTDIR = (
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.461"',
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.462"',
    "../data",
)

PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"

# Query squeletons.
echo_command = (
    'echoscu -ll trace -aec "{}" -aet "{}" {} {}'  # server_AET MY_AET IP port
)
find_command = (
    "findscu -v {} --study -k QueryRetrieveLevel={} -k 0010,0020={} "
    "-k 20,11 -k 10,10 -k 10,1010 -k 0020,000d={} --key 0020,000e={} "
    "--key 0008,103E={} --key 18,1030={} --key 8,22={} "
    "--key 0008,0020={} --key 0010,0010={} --key 10,30={} "
    "--key 8,30 --key 18,1000={} --key 8,60={} --key 8,8={} "
    "--key 8,1030={} --key 8,50={} --key 18,24={}"
)
move_command = (
    'movescu -ll debug {} -aem "{}" -k 0008,0052="PATIENT" --patient '
    "--key 0010,0020={} --key 0020,000d={} --key 0020,000e={} "
    "--key 0008,0020={} --port {} -od {}"
)
move_remote_command = (
    'movescu -ll debug {} -aem "{}" -k 0008,0052="PATIENT" --patient '
    "--key 0010,0020={} --key 0020,000d={} --key 0020,000e={} --key 0008,0020={}"
)


########################################################################################################################
########################################################FUNCTIONS#######################################################
########################################################################################################################


def echo(
    server_address: str = "www.dicomserver.co.uk",
    port: int = 104,
    server_AET: str = "theServertAET",
    AET: str = "AET",
) -> str:
    """Checks that the PACS server can be reached and accepts associations.

    Args:
        server_address: PACS server IP address
        port: PACS server port for incoming requests
        server_AET: PACS server AET
        AET: AET of the calling entity

    Returns:
        string: The log lines

    """
    check_server_address(server_address)
    check_port(port)
    check_AET(server_AET, server=True)
    check_AET(AET)

    command = echo_command.format(server_AET, AET, server_address, port)

    return run(command)


def find(
    AET: str,
    server_address: str = "www.dicomserver.co.uk",
    server_AET: str = "theServerAET",
    port: int = 104,
    QUERYRETRIVELEVEL: str = "SERIES",
    PATIENTID: str = "",
    STUDYUID: str = "",
    SERIESINSTANCEUID: str = "",
    SERIESDESCRIPTION: str = "",
    PROTOCOLNAME: str = "",
    ACQUISITIONDATE: str = "",
    PATIENTNAME: str = "",
    PATIENTBIRTHDATE: str = "",
    STUDYDATE: str = "",
    DEVICESERIALNUMBER: str = "",
    MODALITY: str = "",
    IMAGETYPE: str = "",
    STUDYDESCRIPTION: str = "",
    ACCESSIONNUMBER: str = "",
    SEQUENCENAME: str = "",
) -> str:
    """Builds a query for findscu of QueryRetrieveLevel of series using the parameters passed as arguments.

    Args:
        AET: called AET
        server_address: PACS server IP address
        server_AET: PACS server AET
        port: PACS server port for incoming requests
        QUERYRETRIVELEVEL: query retrieval level which can only take values in {SERIES, STRUDY, PATIENT, IMAGE}
        PATIENTID: patient id
        STUDYUID: study unique idetifier
        SERIESINSTANCEUID: series Instance UID
        SERIESDESCRIPTION: series Description
        PROTOCOLNAME: protocol name
        ACQUISITIONDATE: acquisition date
        PATIENTNAME: patient's name
        PATIENTBIRTHDATE: patient's birth date
        STUDYDATE: study Date
        DEVICESERIALNUMBER: MRI device serial number
        MODALITY: modality
        IMAGETYPE: image type
        STUDYDESCRIPTION: description of the study
        ACCESSIONNUMBER: accession number

    Returns:
        string: The log lines

    """

    check_ids(PATIENTID)
    check_ids(STUDYUID, attribute="Study instance UID")
    check_ids(SERIESINSTANCEUID, attribute="Series instance UID")
    check_port(port)
    check_query_retrieval_level(QUERYRETRIVELEVEL)

    modified_params = replace_default_params(
        PARAMETERS, AET, server_address, server_AET, port
    )
    command = find_command.format(
        modified_params,
        QUERYRETRIVELEVEL,
        PATIENTID,
        STUDYUID,
        SERIESINSTANCEUID,
        SERIESDESCRIPTION,
        PROTOCOLNAME,
        ACQUISITIONDATE,
        STUDYDATE,
        PATIENTNAME,
        PATIENTBIRTHDATE,
        DEVICESERIALNUMBER,
        MODALITY,
        IMAGETYPE,
        STUDYDESCRIPTION,
        ACCESSIONNUMBER,
        SEQUENCENAME,
    )

    return run(command)


def get(
    AET: str,
    STUDYDATE: str,
    server_address: str = "www.dicomserver.co.uk",
    server_AET: str = "theServerAET",
    port: int = 104,
    PATIENTID: str = PATIENTID,
    STUDYINSTANCEUID: str = STUDYINSTANCEUID,
    SERIESINSTANCEUID: str = SERIESINSTANCEUID,
    move_port: int = 4006,
    OUTDIR: str = OUTDIR,
) -> str:
    """Builds a query for movescu.

    Args:
        AET: called AET
        STUDYDATE: study date
        server_address: PACS server IP address
        server_AET: PACS server AET
        port: PACS server port for incoming requests
        PATIENTID: patient id
        STUDYINSTANCEUID: study instance unique idetifier
        SERIESINSTANCEUID: series instance unique identifier
        move_port: port used for movescu command
        OUTDIR: directory of output files

    Returns:
        string: The log lines

    """
    check_ids(PATIENTID)
    check_ids(SERIESINSTANCEUID, attribute="Series instance UID")
    check_ids(STUDYINSTANCEUID, attribute="Study instance UID")
    check_port(move_port)
    check_port(port)

    modified_params = replace_default_params(
        PARAMETERS, AET, server_address, server_AET, port
    )
    command = move_command.format(
        modified_params,
        AET,
        PATIENTID,
        STUDYINSTANCEUID,
        SERIESINSTANCEUID,
        STUDYDATE,
        move_port,
        OUTDIR,
    )
    return run(command)


def move_remote(
    AET: str,
    STUDYDATE: str,
    server_address: str = "www.dicomserver.co.uk",
    server_AET: str = "theServerAET",
    port: int = 104,
    PATIENTID: str = PATIENTID,
    STUDYINSTANCEUID: str = STUDYINSTANCEUID,
    SERIESINSTANCEUID: str = SERIESINSTANCEUID,
    move_AET: str = "theMoveAET",
) -> str:
    """Builds a query for movescu.

    Args:
        AET: called AET
        STUDYDATE: study date.
        server_address: PACS server IP address
        server_AET: PACS server AET
        port: PACS server port for incoming requests
        PATIENTID: patient id
        STUDYINSTANCEUID: study instance unique idetifier.
        SERIESINSTANCEUID: series instance unique identifier
        move_AET: AET where to move the images

    Returns:
        string: The log lines.

    """
    check_ids(PATIENTID)
    check_ids(SERIESINSTANCEUID, attribute="Series instance UID")
    check_ids(STUDYINSTANCEUID, attribute="Study instance UID")
    check_port(port)
    check_AET(move_AET)

    modified_params = replace_default_params(
        PARAMETERS, AET, server_address, server_AET, port
    )
    command = move_remote_command.format(
        modified_params,
        move_AET,
        PATIENTID,
        STUDYINSTANCEUID,
        SERIESINSTANCEUID,
        STUDYDATE,
    )

    return run(command)


def write_file(results: str, file: str = "output.txt") -> None:
    """Writes results in file passed in parameters using the parameters passed as arguments.

    Args:
        results: a str of lines of logs
        file: path to text file where the log lines in results will be written

    """

    if not os.path.exists(file):
        # os.mknod(file) # not cross-platform - unsupported on os X without root
        f = open(file, "w", encoding="utf_8")
    else:
        f = open(file, "a", encoding="utf_8")
    for line in results:
        f.write(str(line) + "\n")
    f.close()


def replace_default_params(
    PARAMETERS: str, AET: str, server_address: str, server_AET: str, port: int
) -> str:
    """Helper function to replace default parameters in queries by new parameters.

    Args:
        PARAMETERS: The string containing default parameters for dicomserver
        AET: Called AET
        server_address: PACS server IP address
        server_AET: PACS server AET
        port: PACS server port for incoming requests
    Returns:
        string: modified parameters with input values.

    """
    check_parameters_inputs(AET, server_address, server_AET, port)

    return (
        PARAMETERS.replace("theServerAET", server_AET)
        .replace(" 104", " " + str(port))
        .replace("88.202.185.144", server_address)
        .replace("MY_AET", AET)
    )


def run(query: str) -> str:
    """Runs the command passed as parameter.

    Args:
        query: query command line to be executed

    Returns:
        string: The log lines

    """
    try:
        # The replace in the line below is necessary for the windows deployment.
        cmd = shlex.split(query.replace("\\", "\\\\"))
        with open("log.txt", "a") as f:
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

        with open("fails.txt", "a") as f:
            f.write(query + "\n")

        print(e.returncode)
        print(e.output)
        lines = ""

    return lines