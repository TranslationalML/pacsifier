#!/usr/bin/env python

# Copyright (C) 2018-2024, University Hospital Center and University of Lausanne (UNIL-CHUV),
# Switzerland & Contributors, All rights reserved.
# This software is distributed under the open-source Apache 2.0 license.

"""`Setup.py` for PACSIFIER."""
from os import path as op
from setuptools import setup


def main():
    """Main function of PACSIFIER ``setup.py``"""
    root_dir = op.abspath(op.dirname(__file__))

    version = None
    cmdclass = {}
    if op.isfile(op.join(root_dir, "pacsifier", "VERSION")):
        with open(op.join(root_dir, "pacsifier", "VERSION")) as vfile:
            version = vfile.readline().strip()

    if version is None:
        version = {}
        with open(op.join(root_dir, "pacsifier", "info.py")) as fp:
            exec(fp.read(), version)
        version = version['__version__']

    # Setup configuration
    setup(
        name="pacsifier",
        version=version,
        cmdclass=cmdclass,
    )


if __name__ == "__main__":
    main()