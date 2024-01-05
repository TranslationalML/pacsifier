"""Tests for the functions in pacsman.cli.convert script."""

from pacsman.cli.convert import process_list


def test_process_list():
    paths = [
        "sub-1234/ses-20170425114510",
        "sub-3456/ses-20170525114500",
        "sub-6788/ses-20170625114500",
    ]
    assert process_list(paths) == [
        ("1234", "20170425114510"),
        ("3456", "20170525114500"),
        ("6788", "20170625114500"),
    ]
