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

"""This module contains functions to execute DCMTK commands."""

import os
import re
import warnings
import shlex
import subprocess
import platform

from pacsifier.core.sanity_checks import (
    check_parameters_inputs,
    check_ids,
    check_server_address,
    check_port,
    check_AET,
    check_query_retrieval_level,
)

warnings.filterwarnings("ignore")

# PHI-bearing DICOM tags in DCMTK --key / -k arguments (values redacted in log files).
_PHI_TAG_RE = re.compile(
    r"(?i)"
    r"((?:--key|-k)\s+)"
    r"(0*10[,\s]+0*(?:20|10|30))"
    r"(=)"
    r"([^\s\"'][^\s]*|\"[^\"]*\"|'[^']*')"
)
_REDACTED = "<REDACTED>"


def _redact_phi_keys(command: str) -> str:
    """Mask PatientID / PatientName / DOB values in a command string."""

    def _replace(m: re.Match) -> str:
        value = m.group(4)
        if value == _REDACTED:
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}{m.group(3)}{_REDACTED}"

    return _PHI_TAG_RE.sub(_replace, command)


def _audit_log_line(cmd: list[str]) -> str:
    """One-line, PHI-free record for log.txt / fails.txt (CodeQL-safe, no query body)."""
    tool = cmd[0] if cmd else "unknown"
    return f"dcmtk tool={tool} (command details not persisted)\n"


def _dcmtk_log_level() -> str:
    """DCMTK ``-ll`` level from ``PACSIFIER_LOG_LEVEL`` (default ``info``)."""
    level = os.environ.get("PACSIFIER_LOG_LEVEL", "info").lower().strip()
    valid = {"trace", "debug", "info", "warn", "error", "fatal", "off"}
    return level if level in valid else "info"


def _dcmtk_timeout_flags() -> str:
    conn = int(os.environ.get("PACSIFIER_CONN_TIMEOUT_SEC", "30"))
    acse = int(os.environ.get("PACSIFIER_ACSE_TIMEOUT_SEC", "30"))
    dimse = int(os.environ.get("PACSIFIER_DIMSE_TIMEOUT_SEC", "60"))
    return f"--timeout {conn} -ta {acse} -td {dimse}"


def _move_retrieve_level_flags() -> str:
    """C-MOVE QueryRetrieveLevel from ``PACSIFIER_RETRIEVE_LEVEL`` (default PATIENT)."""
    retrieve_level = os.environ.get("PACSIFIER_RETRIEVE_LEVEL", "PATIENT").upper()
    if retrieve_level == "SERIES":
        return '-k 0008,0052="SERIES" --patient'
    return '-k 0008,0052="PATIENT" --patient'


# Query default parameters
PATIENT_ID = '"PAT004"'
STUDY_INSTANCE_UID, SERIES_INSTANCE_UID, OUTPUT_DIR = (
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.461"',
    '"1.2.276.0.7230010.3.1.4.2032403683.11008.1512470699.462"',
    ".",
)
PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"

##############################################################################
# FUNCTIONS
##############################################################################


def echo(
    server_address: str = "www.dicomserver.co.uk",
    port: int = 104,
    server_aet: str = "theServertAET",
    aet: str = "AET",
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
    timeout: int = 10,
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
        timeout: time in seconds to wait for a response from the server. Default is 30.

    Returns:
        string: The log lines.

    """
    check_server_address(server_address)
    check_port(port)
    check_AET(server_aet, server=True)
    check_AET(aet)

    ll = _dcmtk_log_level()
    echo_command = (
        f'echoscu -ll {ll} --timeout {timeout} -aec "{server_aet}" '
        f'-aet "{aet}" {server_address} {port}'
    )

    return run(
        query=echo_command,
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
    """Builds a query for findscu of QueryRetrieveLevel of series using the
    parameters passed as arguments.

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

    ll = _dcmtk_log_level()
    find_command = (
        f"findscu -ll {ll} {modified_params} {_dcmtk_timeout_flags()} --study "
        f"-k QueryRetrieveLevel={query_retrieval_level} "
        f"-k 0010,0020={patient_id} "
        f"-k 20,11 -k 10,10 -k 10,1010 -k 0020,000d={study_uid} "
        f"--key 0020,000e={series_instance_uid} "
        f"--key 0008,103E={series_description} "
        f"--key 18,1030={protocol_name} --key 8,22={acquisition_date} "
        f"--key 0008,0020={study_date} --key 0010,0010={patient_name} "
        f"--key 10,30={patient_birthdate} "
        f"--key 8,30 --key 18,1000={device_serial_number} "
        f"--key 8,60={modality} --key 8,8={image_type} "
        f"--key 8,1030={study_description} --key 8,50={accession_number} "
        f"--key 18,24={sequence_name} "
        f"--key 20,1206 --key 20,1208 --key 20,1209"
    )

    return run(
        query=find_command,
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
    move_aet: str = "",
) -> str:
    """Builds a query for movescu.

    Args:
        aet: called AET.
        study_date: study date.
        server_address: PACS server IP address. Default is "www.dicomserver.co.uk".
        server_aet: PACS server AET. Default is "theServerAET".
        port: PACS server port for incoming requests. Default is 104.
        patient_id: patient id. Default is pacsifier.core.execute_commands.patient_id.
        study_instance_uid: study instance unique idetifier. Default is
                          pacsifier.core.execute_commands.study_instance_uid.
        series_instance_uid: series instance unique identifier. Default is
                           pacsifier.core.execute_commands.series_instance_uid.
        move_port: port used for movescu command. Default is 4006.
        output_dir: directory of output files. Default is "." e.g. the current working directory.
        log_dir: Folder for the logs where the log file (log.txt) and
                 the fails file (fails.txt) produced by run() will be written.
                 Default is "./logs" e.g. the logs/ folder in the current working directory.
        move_aet: AET for the C-MOVE destination (-aem). When empty (default),
                  falls back to ``aet`` for backward compatibility.

    Returns:
        string: The log lines.

    """
    check_ids(patient_id)
    check_ids(series_instance_uid, attribute="Series instance UID")
    check_ids(study_instance_uid, attribute="Study instance UID")
    check_port(move_port)
    check_port(port)

    destination_aet = move_aet if move_aet else aet

    modified_params = replace_default_params(
        PARAMETERS, aet, server_address, server_aet, port
    )

    ll = _dcmtk_log_level()
    move_command = (
        f"movescu -ll {ll} {modified_params} {_dcmtk_timeout_flags()}"
        f' -aem "{destination_aet}"'
        f" {_move_retrieve_level_flags()}"
        f" --key 0010,0020={patient_id}"
        f" --key 0020,000d={study_instance_uid}"
        f" --key 0020,000e={series_instance_uid}"
        f" --key 0008,0020={study_date}"
        f" --port {move_port} -od {output_dir}"
    )

    return run(
        query=move_command,
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
        patient_id: patient id. Default is pacsifier.core.execute_commands.patient_id.
        study_instance_uid: study instance unique idetifier. Default is
                          pacsifier.core.execute_commands.study_instance_uid.
        series_instance_uid: series instance unique identifier. Default is
                           pacsifier.core.execute_commands.series_instance_uid.
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

    ll = _dcmtk_log_level()
    move_remote_command = (
        f'movescu -ll {ll} {modified_params} {_dcmtk_timeout_flags()} -aem "{move_aet}" '
        f"{_move_retrieve_level_flags()} "
        f"--key 0010,0020={patient_id} --key 0020,000d={study_instance_uid} "
        f"--key 0020,000e={series_instance_uid} --key 0008,0020={study_date}"
    )

    return run(
        query=move_remote_command,
        log_dir=log_dir,
    )


def upload(
    aet: str,
    dicom_dir: str,
    server_address: str = "www.dicomserver.co.uk",
    server_aet: str = "theServerAET",
    port: int = 4242,
    log_dir: str = os.path.join(OUTPUT_DIR, "logs"),
):
    """Build a query for storescu to upload dicom files to a PACS server.

    Args:
        aet: called AET.
        dicom_dir: directory of dicom files to upload.
        server_address: PACS server IP address. Default is "www.dicomserver.co.uk".
        server_aet: PACS server AET. Default is "theServerAET".
        port: PACS server port for incoming requests. Default is 4242.
        log_dir: Folder for the logs where the log file (log.txt) and
                 the fails file (fails.txt) produced by run() will be written.
                 Default is "./logs" e.g. the logs/ folder in the current working directory.
    """
    check_port(port)
    check_AET(aet)
    check_server_address(server_address)
    check_AET(server_aet, server=True)

    ll = _dcmtk_log_level()
    upload_command = (
        f"storescu -ll {ll} {server_address} {port} "
        f'-aet "{aet}" -aec "{server_aet}" '
        f"--scan-directories {dicom_dir}"
    )

    return run(query=upload_command, log_dir=log_dir)


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


_RE_DIMSE_STATUS = re.compile(r"DIMSE Status\s+:\s*(0x[0-9a-fA-F]+)")
_RE_SUBOPS = {
    name: re.compile(name.capitalize() + r" Suboperations\s+:\s*(\d+)")
    for name in ("completed", "failed", "warning", "remaining")
}


def _last_int(pattern: re.Pattern[str], text: str) -> int | None:
    found = pattern.findall(text)
    return int(found[-1]) if found else None


def _key(cmd_text: str, tag: str) -> str:
    m = re.search(r"--key\s+" + tag + r"=(\S+)", cmd_text)
    return m.group(1) if m else ""


def _move_result_line(cmd_text: str, output: str, reason: str) -> str:
    """Machine-readable C-MOVE verdict for orchestrators (e.g. MiCo series ledger)."""
    final_idx = output.rfind("Received Final Move Response")
    final = final_idx != -1
    chunk = output[final_idx:] if final else ""
    status = _RE_DIMSE_STATUS.findall(chunk)
    if status:
        status_val = status[-1].lower()
    else:
        m = re.search(r"Received Final Move Response\s*\(([A-Za-z]+)", chunk)
        status_val = m.group(1).lower() if m else ""
    fields = {
        "series": _key(cmd_text, "0020,000e"),
        "study": _key(cmd_text, "0020,000d"),
        "patient": _key(cmd_text, "0010,0020"),
        "final": "1" if final else "0",
        "status": status_val,
        "reason": reason,
    }
    for name, rx in _RE_SUBOPS.items():
        v = _last_int(rx, chunk)
        fields[name] = "" if v is None else str(v)
    return "* MOVE_RESULT " + " ".join(f"{k}={v}" for k, v in fields.items())


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
            f.write(_audit_log_line(cmd))
    except ValueError:
        print("* Command parsing error: {}".format(" ".join(cmd)))
        exit()

    try:
        subprocess_timeout = (
            int(os.environ.get("PACSIFIER_SUBPROCESS_TIMEOUT_SEC", "0")) or None
        )
    except ValueError:
        subprocess_timeout = None

    is_move = bool(cmd) and cmd[0] == "movescu"
    cmd_text = " ".join(cmd)

    try:
        if "Windows" in platform.platform():
            completed = subprocess.check_output(
                cmd, stderr=subprocess.PIPE, timeout=subprocess_timeout
            )
            lines = completed.decode("latin1").splitlines()
        else:
            completed = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=True,
                timeout=subprocess_timeout,
            )
            lines = completed.stderr.decode("latin1").splitlines()
        lines = [line.replace("\x00", "") for line in lines]
        if is_move:
            print(_move_result_line(cmd_text, "\n".join(lines), "ok"))
    except subprocess.TimeoutExpired as e:
        print(
            "* Command timed out after {}s: {}".format(
                subprocess_timeout, cmd_text
            )
        )
        if is_move:
            partial = e.stderr if isinstance(e.stderr, bytes) else b""
            print(
                _move_result_line(
                    cmd_text, partial.decode("latin1", errors="replace"), "timeout"
                )
            )
        with open(os.path.join(log_dir, "fails.txt"), "a") as f:
            f.write(_audit_log_line(cmd))
        lines = ""
    except subprocess.CalledProcessError as e:
        print(
            "* Command did not succeed: {}, return code {}".format(
                cmd_text, e.returncode
            )
        )
        print("* Output: {}".format(e.stderr))
        if is_move:
            err = e.stderr if isinstance(e.stderr, bytes) else b""
            print(
                _move_result_line(
                    cmd_text,
                    err.decode("latin1", errors="replace"),
                    f"rc{e.returncode}",
                )
            )

        with open(os.path.join(log_dir, "fails.txt"), "a") as f:
            f.write(_audit_log_line(cmd))

        print(e.returncode)
        print(e.output)
        lines = ""

    return lines
