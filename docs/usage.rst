.. _cmdusage:

***********************
Commandline Usage
***********************

PACSMAN is a commandline tool that can be run in a variety of ways, providing a set of command-line interface (CLI) commands, which can be run directly in a shell or via a Docker container, for interacting with a PACS server and manipulating DICOM files.

It consists of the following commands:

* ``pacsman``: The main command, which can be used to interact with a PACS server and manipulate DICOM files.
* ``pacsman-anonymize-dicoms``: Anonymize DICOM files.
* ``pacsman-create-dicomdir``: Create a DICOMDIR file.
* ``pacsman-get-pseudonyms``: Get pseudonyms for a list of DICOM files.
* ``pacsman-move-dumps``: Move DICOM files from a PACS server to a local directory.
* ``pacsman-add-karnak-tags``: Add Karnak tags to DICOM files.
* ``pacsman-extract-carestream-report``: Extract Carestream reports from DICOM files.
* ``pacsman-convert``: Convert DICOM files to another format.


In the following sections, we will describe how to run these commands in a shell and in a Docker container.

Running `PACSMAN` commands in a shell
=====================================

``pacsman`` command
-------------------

.. argparse::
		:ref: pacsman.cli.pacsman.get_parser
		:prog: pacsman

``pacsman-anonymize-dicoms`` command
-------------------------------------

.. argparse::
		:ref: pacsman.cli.anonymize_dicoms.get_parser
		:prog: pacsman-anonymize_dicoms

``pacsman-create-dicomdir`` command
-------------------------------------

.. argparse::
		:ref: pacsman.cli.create_dicomdir.get_parser
		:prog: pacsman-create-dicomdir

``pacsman-get-pseudonyms`` command
-------------------------------------

.. argparse::
		:ref: pacsman.cli.get_pseudonyms.get_parser
		:prog: pacsman-get-pseudonyms

``pacsman-move-dumps`` command
-------------------------------------

.. argparse::
		:ref: pacsman.cli.move_dumps.get_parser
		:prog: pacsman-move-dumps

``pacsman-add-karnak-tags`` command
-------------------------------------

.. argparse::
		:ref: pacsman.cli.add_karnak_tags.get_parser
		:prog: pacsman-add-karnak-tags

``pacsman-extract-carestream-report`` command
----------------------------------------------

.. argparse::
		:ref: pacsman.cli.extract-carestream_report.get_parser
		:prog: pacsman-extract-carestream-report

``pacsman-convert`` command
----------------------------

.. argparse::
		:ref: pacsman.cli.convert.get_parser
		:prog: pacsman-convert


.. _cmdusage-docker:

Running `PACSMAN` commands in Docker
====================================

In this section, we provide examples to run each of the ``PACSMAN`` commands in the Docker container.

``pacsman`` command
-------------------

.. code-block:: bash

        docker run --rm -it \
            -v /path/to/dicom/files:/data:ro \
            -v /path/to/output:/output:rw \
            -v /path/to/config:/config:ro \
            -v /path/to/logs:/logs:rw
            -v /path/to/pseudonyms:

TODO
