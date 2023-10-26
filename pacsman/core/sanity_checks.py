from datetime import datetime
from typing import Dict

# from urllib.parse import urlparse
# from urllib.request import urlopen
# from urllib.error import URLError, HTTPError
# import requests
# from ipaddress import ip_address
# import re


def check_ip(ip_address: str) -> None:
    """Check if an ip adress is valid.

    Args:
            ip_address: IP address

    Raises:
        ValueError if it is not valid
    """
    message = "Invalid IP address"
    if len(ip_address.split(".")) != 4:
        raise ValueError(message)
    ip_splitted = ip_address.split(".")

    for i in ip_splitted:
        if i == "" or len(i) > 3:
            raise ValueError(message)
        try:
            int(i)
        except ValueError:
            raise ValueError(message)
    return


def check_server_address(server_address: str) -> None:
    """Check if a server address is valid.

    Args:
        server_address: server address

    Raises:
        ValueError if it is not valid

    """
    # Handle IP address
    # match = re.match(r"[0-9,a-z,A-z]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", server_address)
    # if bool(match):
    if not server_address.split(".")[-1].isalpha():
        check_ip(server_address)
    # else:  # Handle URL
    #     response = requests.get(server_address)
    #     if response.status_code < 400:
    #         raise ValueError(f"Invalid server address {server_address}: ")
    #     # try:
    #     #     print(f"Parse server address: {server_address}")
    #     #     u = urlopen(server_address)
    #     #     print(f"Parse result: {u.response}")
    #     # except HTTPError as e:
    #     #     raise HTTPError(f"HTTP Error {e.code}: {e.reason}")
    #     # except URLError as e:
    #     #     raise ValueError(f"Invalid server address: {e.reason}")
    return


def check_port(port: int) -> None:
    """Check if a port value is valid.

    Args:
        port: port number

    Raises:
        ValueError if it is not valid

    """
    if port > 65535:
        raise ValueError("Port number is too big!")
    if port < 1:
        raise ValueError("Port number is smaller or equal to zero!")
    return


def check_AET(AET: str, server=False) -> None:
    """Check the validity of an application entity title (AET).

    Args:
        AET: application entity title
        server: boolean indicating if it is a AE title of a server or not

    Raises:
        ValueError if it is not valid and use a boolean to print a relevant error message

    """
    add = ""
    if server:
        add = "Server"
    if AET == "":
        raise ValueError("Empty " + add + " AET passed")
    if len(AET) > 16:
        raise ValueError(add + "AET is too long")
    return


def check_parameters_inputs(
    AET: str, server_address: str, server_AET: str, port: int
) -> None:
    """Check if the parameters are valid using helper functions.

    Args:
            AET: called AET
            server_address: PACS server IP address
            server_AET: PACS server AET
            port: port

    Raises:
        ValueError if at least one parameter is invalid

    """
    check_AET(AET)
    check_AET(server_AET, server=True)
    check_port(port)
    check_server_address(server_address)

    return


def check_ids(uid: str, attribute: str = "Patient ID") -> None:
    """Check if a patient ID is valid.

    Args:
        uid: unique identifier
        attribute: attribute name

    Raises:
        ValueError if it is not valid and print a relevant error message using the argument called attribute

    """

    if len(uid) > 64:
        raise ValueError(attribute + " is too long")
    return


def check_filter(filter_text: str) -> None:
    """Check if an additional input filter is valid.

    Args:
        filter_text: additional attribute to the query command

    """
    if len(filter_text.split("=")) != 2:
        raise ValueError("Invalid filter input.")


def check_tuple(tuple_: Dict[str, str]) -> None:
    """Check that the table has an acceptable input parameters.

    Args:
        tuple_: dictionary that contains all parameters for query

    """
    empty = True
    for item in tuple_.values():
        if str(item) == "*":
            raise ValueError("Can't use * for inputs !")
        if len(str(item)) > 0:
            empty = False

    if empty:
        raise ValueError("Empty line in table ! ")


def check_date_range(date: str) -> None:
    """Check that a date (possibly a date range) is valid.

    Args:
        date: date or date range to be checked

    """
    if date == "":
        return
    if len(date) == 17:
        if len(date.split("-")) != 2:
            raise ValueError("Invalid date range input!")
        dates = date.split("-")

        check_date(dates[0])
        check_date(dates[1])
    else:
        check_date(date)
    return


def check_date(date: str) -> None:
    """Check that a date is valid.

    Args:
        date: date to be checked

    """
    if date == "":
        return
    if len(date) != 8:
        raise ValueError("Invalid date input")
    try:
        int(date)
    except ValueError:
        raise ValueError("Date must contain only numeric characters!")
    year, month, day = int(date[:4]), int(date[4:6]), int(date[6:])

    if year < 1900 or year > datetime.now().year:
        raise ValueError("Invalid year range!")
    if month not in range(1, 13):
        raise ValueError("Invalid month range!")
    if day not in range(1, 32):
        raise ValueError("Invalid day value!")
    return


def check_config_file(config_file: Dict[str, str]) -> None:
    """Check that the config file passed as a parameter is valid or not.

    Args:
        dict: dictionary loaded from the config json file

    """
    items = set(config_file.keys())
    valid_keys = [
        "server_address",
        "port",
        "server_AET",
        "AET",
        "move_AET",
        "move_port",
        "batch_size",
        "batch_wait_time",
    ]
    if items != set(valid_keys):
        raise ValueError(
            "Invalid config file! Must contain these and only these keys: "
            + " ".join(valid_keys)
        )


def check_query_retrieval_level(query_retrieval_level: str) -> None:
    valid_levels = ["SERIES", "PATIENT", "IMAGE", "STUDY"]
    if query_retrieval_level not in valid_levels:
        raise ValueError("Invalid query retrieval level ! ")
