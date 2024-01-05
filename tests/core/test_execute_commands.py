"""Tests for the functions of the execute_commands module."""

import pytest

from pacsman.core.execute_commands import echo, find, get, replace_default_params


def test_echo_invalid_inputs():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    with pytest.raises(ValueError):
        echo(port=0)

    with pytest.raises(ValueError):
        echo(port=65536)

    with pytest.raises(ValueError):
        echo(port=0)

    with pytest.raises(ValueError):
        echo(server_AET=dummy_long_string)

    with pytest.raises(ValueError):
        echo(server_AET="")

    with pytest.raises(ValueError):
        echo(AET=dummy_long_string)

    with pytest.raises(ValueError):
        echo(AET="")

    with pytest.raises(ValueError):
        echo(server_address="128.132.185.16.1")

    with pytest.raises(ValueError):
        echo(server_address="128.s132.185.16")

    with pytest.raises(ValueError):
        echo(server_address="128.132..16")

    with pytest.raises(ValueError):
        echo(server_address="128.132.1855.16")


def test_find_invalid_inputs():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    with pytest.raises(ValueError):
        find("", "19930911")

    with pytest.raises(ValueError):
        find("AET", "19930911", port=0)

    with pytest.raises(ValueError):
        find("AET", "19930911", port=65536)

    with pytest.raises(ValueError):
        find("AET", "19930911", port=0)

    with pytest.raises(ValueError):
        find("AET", "19930911", PATIENTID=dummy_long_string)

    with pytest.raises(ValueError):
        find("AET", "19930911", STUDYUID=dummy_long_string, PATIENTID="PAT004")

    with pytest.raises(ValueError):
        find("AET", "19930911", server_AET="dummyserverAETdummyserverAETdummyserverAET")

    with pytest.raises(ValueError):
        find("AET", "19930911", server_AET="")

    with pytest.raises(ValueError):
        find("dummyAETdummyAETdummyAET", "19930911")

    with pytest.raises(ValueError):
        find("AET", STUDYDATE="19930911", server_address="128.132.185.16.1")

    with pytest.raises(ValueError):
        find("AET", STUDYDATE="19930911", server_address="128.s132.185.16")

    with pytest.raises(ValueError):
        find("AET", STUDYDATE="19930911", server_address="128.132..16")

    with pytest.raises(ValueError):
        find("AET", STUDYDATE="19930911", server_address="128.132.1855.16")


def test_get_invalid_inputs():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    with pytest.raises(ValueError):
        get("", "19930911")

    with pytest.raises(ValueError):
        get("AET", "19930911", port=0)

    with pytest.raises(ValueError):
        get("AET", "19930911", port=65536)

    with pytest.raises(ValueError):
        get("AET", "19930911", port=0)

    with pytest.raises(ValueError):
        get("AET", "19930911", PATIENTID=dummy_long_string)

    with pytest.raises(ValueError):
        get("AET", "19930911", server_AET="dummyserverAETdummyserverAETdummyserverAET")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_AET="")

    with pytest.raises(ValueError):
        get("AET", "19930911", STUDYINSTANCEUID=dummy_long_string)

    with pytest.raises(ValueError):
        get("AET", "19930911", SERIESINSTANCEUID=dummy_long_string)

    with pytest.raises(ValueError):
        get("dummyAETdummyAETdummyAET", "19930911")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_address="128.132.185.16.1")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_address="128.s132.185.16")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_address="128.132..16")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_address="128.132.1855.16")


def test_replace_default_parameters():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    PARAMETERS = "88.202.185.144 104 -aec theServerAET -aet MY_AET"
    modified = "127.0.0.1 80 -aec Hello -aet Hello_Back"

    assert (
        replace_default_params(PARAMETERS, "Hello_Back", "127.0.0.1", "Hello", 80)
        == modified
    )

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, dummy_long_string, "127.0.0.1", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, dummy_long_string, "127.0.0.1", "Hello", -1)
    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "127.0.0.1", dummy_long_string, 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "127.0.0554.1", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "California Dreaming", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "124.20.564.45.45", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "214..54.454", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "", "214.1.54.454", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(PARAMETERS, "AET", "214.54.1.1", "", 80)
