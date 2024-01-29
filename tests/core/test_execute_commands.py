# Copyright (C) 2018-2024, University Hospital Center and University of Lausanne (UNIL-CHUV),
# Switzerland & Contributors, All rights reserved.
# This software is distributed under the open-source Apache 2.0 license.

"""Tests for the functions of the execute_commands module."""

import pytest

from pacsman.core.execute_commands import echo, find, get, replace_default_params, run


def test_echo_invalid_inputs():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    with pytest.raises(ValueError):
        echo(port=0)

    with pytest.raises(ValueError):
        echo(port=65536)

    with pytest.raises(ValueError):
        echo(server_aet=dummy_long_string)

    with pytest.raises(ValueError):
        echo(server_aet="")

    with pytest.raises(ValueError):
        echo(aet=dummy_long_string)

    with pytest.raises(ValueError):
        echo(aet="")

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
        find("AET", "19930911", patient_id=dummy_long_string)

    with pytest.raises(ValueError):
        find("AET", "19930911", study_uid=dummy_long_string, patient_id="PAT004")

    with pytest.raises(ValueError):
        find("AET", "19930911", server_aet="dummyserverAETdummyserverAETdummyserverAET")

    with pytest.raises(ValueError):
        find("AET", "19930911", server_aet="")

    with pytest.raises(ValueError):
        find("dummyAETdummyAETdummyAET", "19930911")

    with pytest.raises(ValueError):
        find("AET", study_date="19930911", server_address="128.132.185.16.1")

    with pytest.raises(ValueError):
        find("AET", study_date="19930911", server_address="128.s132.185.16")

    with pytest.raises(ValueError):
        find("AET", study_date="19930911", server_address="128.132..16")

    with pytest.raises(ValueError):
        find("AET", study_date="19930911", server_address="128.132.1855.16")


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
        get("AET", "19930911", patient_id=dummy_long_string)

    with pytest.raises(ValueError):
        get("AET", "19930911", server_aet="dummyserverAETdummyserverAETdummyserverAET")

    with pytest.raises(ValueError):
        get("AET", "19930911", server_aet="")

    with pytest.raises(ValueError):
        get("AET", "19930911", study_instance_uid=dummy_long_string)

    with pytest.raises(ValueError):
        get("AET", "19930911", series_instance_uid=dummy_long_string)

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
    parameters = "88.202.185.144 104 -aec theServerAET -aet MY_AET"
    modified = "127.0.0.1 80 -aec Hello -aet Hello_Back"

    assert (
        replace_default_params(parameters, "Hello_Back", "127.0.0.1", "Hello", 80)
        == modified
    )

    with pytest.raises(ValueError):
        replace_default_params(parameters, dummy_long_string, "127.0.0.1", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, dummy_long_string, "127.0.0.1", "Hello", -1)
    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "127.0.0.1", dummy_long_string, 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "127.0.0554.1", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "California Dreaming", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "124.20.564.45.45", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "214..54.454", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "", "214.1.54.454", "Hello", 80)

    with pytest.raises(ValueError):
        replace_default_params(parameters, "AET", "214.54.1.1", "", 80)


def test_run():
    assert [] == run("echo California Dreaming.", log_dir="/tests/logs")
