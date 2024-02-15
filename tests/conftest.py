"""Pytest configuration file with declarations of fixtures shared across all tests."""

import os
import shutil
import pytest


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def test_dir():
    """Clean the tmp directory and return the path to the test directory.
    
    This fixture is used to clean at the session scope level the tmp directory
    before running the tests. It is also used to get the path to the test
    directory, which is used to create temporary files and directories during
    the tests.
    """
    if os.path.isdir(os.path.join(TEST_DIR, "tmp")):
        shutil.rmtree(os.path.join(TEST_DIR, "tmp"))

    return TEST_DIR


@pytest.fixture(scope="session")
def dummy_long_string():
    return (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
