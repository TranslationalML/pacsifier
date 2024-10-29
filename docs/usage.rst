.. _cmdusage:

***********************
Commandline Usage
***********************

PACSIFIER is a commandline tool that can be run in a variety of ways, providing a set of command-line interface (CLI) commands, which can be run directly in a shell or via a Docker container, for interacting with a PACS server and manipulating DICOM files.

It consists of the following commands:

* ``pacsifier``: The main command, which can be used to interact with a PACS server and manipulate DICOM files.
* ``pacsifier-anonymize-dicoms``: Anonymize DICOM files.
* ``pacsifier-create-dicomdir``: Create a DICOMDIR file.
* ``pacsifier-get-pseudonyms``: Get pseudonyms for a list of DICOM files.
* ``pacsifier-move-dumps``: Move DICOM files from a PACS server to a local directory.
* ``pacsifier-add-karnak-tags``: Add Karnak tags to DICOM files.
* ``pacsifier-extract-carestream-report``: Extract Carestream reports from DICOM files.

In the following sections, we will describe how to run these commands in a shell and in a Docker container.

Running `PACSIFIER` commands in a shell
=======================================

``pacsifier`` command
----------------------

.. argparse::
		:ref: pacsifier.cli.pacsifier.get_parser
		:prog: pacsifier

``pacsifier-anonymize-dicoms`` command
--------------------------------------

.. argparse::
		:ref: pacsifier.cli.anonymize_dicoms.get_parser
		:prog: pacsifier-anonymize_dicoms

``pacsifier-create-dicomdir`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.create_dicomdir.get_parser
		:prog: pacsifier-create-dicomdir

``pacsifier-get-pseudonyms`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.get_pseudonyms.get_parser
		:prog: pacsifier-get-pseudonyms

``pacsifier-move-dumps`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.move_dumps.get_parser
		:prog: pacsifier-move-dumps

``pacsifier-add-karnak-tags`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.add_karnak_tags.get_parser
		:prog: pacsifier-add-karnak-tags


.. _cmdusage-docker:

Running `PACSIFIER` commands in Docker
======================================

In this section, we provide examples to run each of the ``PACSIFIER`` commands in the Docker container.

``pacsifier`` command
---------------------

.. code-block:: bash

        docker run -it --rm -v /home/my_user/my_dir:/base --entrypoint "conda" pacsifier:1.0.0 run -n pacsifier_minimal python anonymize_Dicoms.py --in_folder /base/files-directory --out_folder /base/anonymized-files-directory --new_ids /base/my_new_ids.json --delete_identifiable --fuzz_acq_dates
