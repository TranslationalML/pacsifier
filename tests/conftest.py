import os
import subprocess
import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def test_dir():
    return TEST_DIR
