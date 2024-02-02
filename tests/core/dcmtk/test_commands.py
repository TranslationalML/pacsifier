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

"""Tests for the functions of the `pacsman.core.execute_commands` module."""

import os
import pytest

from pacsman.core.dcmtk.commands import (
    echo, find, get, upload, replace_default_params, run
)


def test_echo_invalid_inputs(dummy_long_string):
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


def test_find_invalid_inputs(dummy_long_string):
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


def test_get_invalid_inputs(dummy_long_string):
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


def test_upload_invalid_inputs(test_dir):
    
    with pytest.raises(ValueError):
        upload("", os.path.join(test_dir, "test_data", "dicomseries-not-existing"))
    
    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), port=0)

    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), port=65536)

    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_address="128.132.185.16.1")

    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_address="128.s132.185.16")
    
    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_address="128.132..16")
    
    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_address="128.132.1855.16")

    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_aet="dummyserverAETdummyserverAETdummyserverAET")
    
    with pytest.raises(ValueError):
        upload("AET", os.path.join(test_dir, "test_data", "dicomseries"), server_aet="")


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
