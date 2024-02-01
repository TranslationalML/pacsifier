"""Pytest configuration file with declarations of fixtures shared across all tests."""

import os
import pytest


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def test_dir():
    return TEST_DIR


@pytest.fixture(scope="session")
def dummy_long_string():
    return (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
