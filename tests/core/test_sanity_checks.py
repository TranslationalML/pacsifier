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

"""Tests for the functions of the `pacsifier.core.sanity_checks` module."""

import pytest

from pacsifier.core.sanity_checks import (
    check_config_parameters,
    check_query_retrieval_level,
    check_server_address,
    check_port,
    check_AET,
    check_parameters_inputs,
    check_ids,
    check_filter,
    check_query_attributes,
    check_date,
    check_date_range,
)


def test_check_config_parameters_invalid():
    with pytest.raises(ValueError):
        check_config_parameters({"California Dreaming": 1})


def test_check_config_parameters_valid():
    check_config_parameters({
            "server_address": "localhost",
            "port": 4444,
            "server_AET": "SCU_STORE",
            "AET": "PACSIFIER_SCU",
            "move_port": 11112,
            "move_AET": "PACSIFIER_SCU",
            "batch_size": 30,
            "batch_wait_time": 10
        })
    

def test_check_config_parameters_invalid_values():
    with pytest.raises(ValueError):
        check_config_parameters({
            "server_address": "localhost",
            "port": 4444,
            "server_AET": "SCU_STORE",
            "AET": "PACSIFIER_SCU",
            "move_port": "11112a",  # Invalid port should be an int and not a string
            "move_AET": "PACSIFIER_SCU",
            "batch_size": 30,
            "batch_wait_time": 10
        })
    with pytest.raises(ValueError):
        check_config_parameters({
            "server_address": "localhost",
            "port": 4444,
            "server_AET": "SCU_STORE",
            "AET": "PACSIFIER_SCU",
            "move_port": 11112,
            "move_AET": "PACSIFIER_SCU",
            "batch_size": "30y",  # Invalid batch size should be an int and not a string
            "batch_wait_time": 10
        })
    with pytest.raises(ValueError):
        check_config_parameters({
            "server_address": "localhost",
            "port": 4444,
            "server_AET": "SCU_STORE",
            "AET": "PACSIFIER_SCU",
            "move_port": 11112,
            "move_AET": "PACSIFIER_SCU",
            "batch_size": 30,
            "batch_wait_time": "10y"  # Invalid batch wait time
        })


def test_check_query_retrieval_level():
    with pytest.raises(ValueError):
        check_query_retrieval_level({"Hello"})


def test_sanity_checks():
    dummy_long_string = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    with pytest.raises(ValueError):
        check_server_address("California Dreaming")

    with pytest.raises(ValueError):
        check_server_address("128.132.185.16.1")

    with pytest.raises(ValueError):
        check_server_address("128.s132.185.16")

    with pytest.raises(ValueError):
        check_server_address("128.132..16")

    with pytest.raises(ValueError):
        check_server_address("128.132.1855.16")

    with pytest.raises(ValueError):
        check_server_address("124.20.564.45.45")

    with pytest.raises(ValueError):
        check_port(14785425)

    with pytest.raises(ValueError):
        check_port(-2)

    with pytest.raises(ValueError):
        check_AET(dummy_long_string)

    with pytest.raises(ValueError):
        check_parameters_inputs(dummy_long_string, "1.1.1.1", "Hello", 80)

    with pytest.raises(ValueError):
        check_parameters_inputs("hello", "1.1.1.1", dummy_long_string, 80)

    with pytest.raises(ValueError):
        check_parameters_inputs("AET", "1.1.1.1", "Hello", -80)

    with pytest.raises(ValueError):
        check_parameters_inputs("AET", "1.1.1.1", "Hello", 100000000)

    with pytest.raises(ValueError):
        check_parameters_inputs("hello", "1.1.1.1.", "teff", 80)

    with pytest.raises(ValueError):
        check_parameters_inputs("hello", "1.1s.1.1", "teff", 80)

    with pytest.raises(ValueError):
        check_parameters_inputs("hello", "1..1.1", "teff", 80)

    with pytest.raises(ValueError):
        check_parameters_inputs("hello", "California Dreaming", "teff", 80)

    with pytest.raises(ValueError):
        check_ids(dummy_long_string)

    with pytest.raises(ValueError):
        check_filter("hello")

    with pytest.raises(ValueError):
        check_query_attributes({"California": "*", "Dreaming": 1})

    with pytest.raises(ValueError):
        check_query_attributes({"California": "", "Dreaming": ""})

    with pytest.raises(ValueError):
        check_date("18930402")

    with pytest.raises(ValueError):
        check_date("19934402")

    with pytest.raises(ValueError):
        check_date("19930472")

    with pytest.raises(ValueError):
        check_date("189304029")

    with pytest.raises(ValueError):
        check_date("1804029")

    with pytest.raises(ValueError):
        check_date("dakdjak")

    assert check_date("") == None
    assert check_date("20180825") == None
    assert check_date_range("") == None
    assert check_date_range("20180825") == None

    with pytest.raises(ValueError):
        check_date_range("18930402-20180722")

    with pytest.raises(ValueError):
        check_date_range("19930825-19934402")

    with pytest.raises(ValueError):
        check_date_range("19930825-19930472")

    with pytest.raises(ValueError):
        check_date_range("19930825-189304029")

    with pytest.raises(ValueError):
        check_date_range("19930825-1804029")

    with pytest.raises(ValueError):
        check_date_range("19930825-dakdjak")
