.. _cmdusage:

***********************
Commandline Usage
***********************

``PACSIFIER`` is a commandline tool that can be run in a variety of ways, providing a set of command-line interface (CLI) commands, which can be run directly in a shell or via a Docker container, for interacting with a PACS server and manipulating DICOM files.

It consists of the following commands:

* ``pacsifier``: The main command, which can be used to interact with a PACS server and manipulate DICOM files.
* ``pacsifier-anonymize``: Anonymize DICOM files.
* ``pacsifier-create-dicomdir``: Create a DICOMDIR file.
* ``pacsifier-get-pseudonyms``: Get pseudonyms for a list of DICOM files.
* ``pacsifier-move-csv``: Move CSV info dumps to a separate folder.
* ``pacsifier-add-karnak-tags``: Add Karnak tags to DICOM files.
* ``pacsifier-extract-carestream-report``: Extract Carestream reports from DICOM files.

In the following sections, we will describe the configuration files, how to run these commands in a shell, and how to run them in a Docker container.


.. _config-file:

Configuration File
==================

PACSIFIER requires a JSON configuration file that specifies the PACS server connection parameters.

.. code-block:: json

    {
        "server_address": "PACS server IP or hostname",
        "port": 104,
        "server_AET": "SERVER_AET",
        "AET": "YOUR_AET",
        "move_AET": "MOVE_DESTINATION_AET",
        "move_port": 11112,
        "batch_size": 30,
        "batch_wait_time": 10,
        "karnak_address": "KARNAK_IP_OR_HOSTNAME",
        "karnak_port": 104,
        "karnak_aet": "KARNAK_AET",
        "pynetdicom_address": "0.0.0.0",
        "pynetdicom_port": 11112,
        "pynetdicom_aet": "PACSIFIER"
    }

.. list-table:: Configuration keys
   :header-rows: 1
   :widths: 25 15 60

   * - Key
     - Type
     - Description
   * - ``server_address``
     - string
     - PACS server IP address or hostname
   * - ``port``
     - integer
     - PACS server port number for incoming requests
   * - ``server_AET``
     - string
     - PACS server Application Entity Title (max 16 characters)
   * - ``AET``
     - string
     - Your local station Application Entity Title (max 16 characters)
   * - ``move_AET``
     - string
     - AET of the remote move destination
   * - ``move_port``
     - integer
     - Port on the move destination to receive images (C-MOVE)
   * - ``batch_size``
     - integer
     - Number of series to download before pausing
   * - ``batch_wait_time``
     - number
     - Sleep time (in seconds) after each batch
   * - ``karnak_address``
     - string
     - Karnak destination host used by ``--karnak`` mode
   * - ``karnak_port``
     - integer
     - Karnak destination port used by ``--karnak`` mode
   * - ``karnak_aet``
     - string
     - Karnak called AE title (``-aec``)
   * - ``pynetdicom_address``
     - string
     - Local bind address for the internal listener used in ``--karnak`` mode
   * - ``pynetdicom_port``
     - integer
     - Local listener port for incoming C-STORE objects from Karnak flow
   * - ``pynetdicom_aet``
     - string
     - Local listener AE title and C-MOVE destination (required in ``--karnak`` mode)

.. note::
    The AET and corresponding IP of the workstation should be declared on the PACS server, including the storeable attribute.

.. tip::
    **Migrating from PACSMAN?** Update the following key names and types:

    * ``server_ip`` → ``server_address``
    * ``port``: string → integer
    * ``move_port``: string → integer
    * ``batch_size``: string → integer
    * ``batch_wait_time``: string → integer


.. _query-file:

Query File
==========

The query file is a ``.csv`` file that specifies which DICOM data to query from the PACS server. It can include one or many of the following columns:

.. list-table:: Supported query columns
   :header-rows: 1
   :widths: 30 70

   * - Column Name
     - Description
   * - ``StudyDate``
     - Study date in ``YYYYMMDD`` format. Date ranges are supported (e.g., ``20150201-20160201``).
   * - ``StudyTime``
     - Study time in ``HHMMSS`` format (e.g., ``140500`` for 14:05:00).
   * - ``PatientID``
     - The patient ID.
   * - ``PatientName``
     - The patient name. Not recommended as there is no clear standard for how names are stored.
   * - ``PatientBirthDate``
     - Patient birth date in ``YYYYMMDD`` format. Date ranges are **not** supported.
   * - ``SeriesDescription``
     - The series description.
   * - ``ProtocolName``
     - The protocol name.
   * - ``StudyInstanceUID``
     - The Study Instance UID.
   * - ``SeriesInstanceUID``
     - The Series Instance UID.
   * - ``Modality``
     - The modality (e.g., ``CT``, ``MR``).
   * - ``AcquisitionDate``
     - The acquisition date.
   * - ``DeviceSerialNumber``
     - The device serial number.
   * - ``SeriesNumber``
     - The series number.
   * - ``StudyDescription``
     - The study description.
   * - ``AccessionNumber``
     - The accession number.
   * - ``SequenceName``
     - The sequence name.
   * - ``ImageType``
     - The image type. **Note:** Using this filter significantly slows down queries. Use only if absolutely necessary.

The query file can be built in Excel and exported to ``.csv`` format.

**Important notes:**

* If a cell in a row is empty, that attribute is omitted from the query for that row.
* The wildcard ``*`` alone is **not** accepted. However, it can be used with other characters (e.g., ``BEAT_SelfNav*``).
* Series folders are named after their Series Description. If a DICOM image has no Series Description, it is stored in a folder called ``No_series_description``.

Query File Examples
-------------------

**Example 1** — Query by date and patient ID:

.. code-block:: text

    StudyDate,PatientID
    20150512,123421
    ,45322
    20180102,

This retrieves: images for patient 123421 from 12/05/2015, all images for patient 45322, and all images from 02/01/2018.

**Example 2** — Date range with patient ID:

.. code-block:: text

    StudyDate,PatientID
    20150512-20150612,124588

Retrieves images for patient 124588 with study dates between 12/05/2015 and 12/06/2015.

**Example 3** — Wildcard protocol name:

.. code-block:: text

    ProtocolName,Modality,PatientBirthDate
    BEAT_SelfNav*,CT,19920611

Retrieves all CT images with protocol names starting with ``BEAT_SelfNav`` for patients born on 11/06/1992.


Count-only metadata query
-------------------------

Use ``--count`` to query PACS metadata only (no image retrieval). It issues
C-FIND requests at the series level and writes one row per series to
``<output_dir>/count_results.csv``, then prints a per-patient summary.

.. code-block:: bash

    pacsifier --count --queryfile query.csv --config config.json --out_directory ./output

The output CSV file contains the following columns:

- ``PatientID``
- ``StudyDate``
- ``SeriesDescription``
- ``NumberOfInstances``

Results are written **continuously** as each query row is processed. If the run
is interrupted, restart with ``--resume`` to skip already-completed query rows:

.. code-block:: bash

    pacsifier --count --resume --queryfile query.csv --config config.json --out_directory ./output

Typical console output:

.. code-block:: text

    Counting element number 1...
      -> 18 series found.
    Counting element number 2...
      -> 5 series found.
    ...
    Done. Results written to: ./output/count_results.csv


Karnak forwarding
-----------------

Use ``--karnak`` to send C-MOVE requests to Karnak and receive returned files
through the built-in pynetdicom listener.

.. code-block:: bash

    pacsifier --karnak --queryfile query.csv --config config.json --out_directory ./output

To generate commands without executing them, use ``--command_file``:

.. code-block:: bash

    pacsifier --karnak --queryfile query.csv --config config.json --command_file ./karnak_commands.txt

You can override Karnak config values from the CLI:

.. code-block:: bash

    pacsifier --karnak -q query.csv -c config.json \
      --karnak_address 10.1.2.3 --karnak_port 104 --karnak_aet KARNAK \
      --pynetdicom_address 0.0.0.0 --pynetdicom_port 11112 --pynetdicom_aet PACSIFIER

Standalone listener entrypoint:

.. code-block:: bash

    pacsifier-pynetdicom-listener --address 0.0.0.0 --port 11112 --aet PACSIFIER --output_dir ./output


Running ``PACSIFIER`` commands in a shell
=========================================

``pacsifier`` command
----------------------

.. argparse::
		:ref: pacsifier.cli.pacsifier.get_parser
		:prog: pacsifier

``pacsifier-anonymize`` command
--------------------------------------

.. argparse::
		:ref: pacsifier.cli.anonymize_dicoms.get_parser
		:prog: pacsifier-anonymize

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

``pacsifier-move-csv`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.move_dumps.get_parser
		:prog: pacsifier-move-csv

``pacsifier-add-karnak-tags`` command
-------------------------------------

.. argparse::
		:ref: pacsifier.cli.add_karnak_tags.get_parser
		:prog: pacsifier-add-karnak-tags

``pacsifier-extract-carestream-report`` command
-----------------------------------------------

.. argparse::
		:ref: pacsifier.cli.extract_carestream_report.get_parser
		:prog: pacsifier-extract-carestream-report

``pacsifier-pynetdicom-listener`` command
-----------------------------------------

.. argparse::
		:ref: pacsifier.cli.pynetdicom_listener.get_parser
		:prog: pacsifier-pynetdicom-listener


.. _cmdusage-docker:

Running ``PACSIFIER`` commands in Docker
========================================

The Docker image entrypoint runs the provided command in the ``pacsifier_minimal`` conda environment. You can use the Docker wrapper scripts (recommended) or call the CLI commands directly.

Recommended (wrapper scripts)
-----------------------------

.. code-block:: bash

		docker_pacsifier -c config.json -q query.csv -d /output --save
		docker_pacsifier -c config.json -q query.csv -d /output --count

See :ref:`docker_wrappers` for the full list of wrapper scripts and examples.

Direct Docker invocation
------------------------

.. code-block:: bash

		docker run --rm --net=host -v /path/to/my_dir:/base \
			quay.io/translationalml/pacsifier:latest \
			pacsifier --save --info --queryfile /base/my_query.csv \
			--config /base/my_config.json --out_directory /base/my_output_dir

		docker run --rm --net=host -v /path/to/my_dir:/base \
			quay.io/translationalml/pacsifier:latest \
			pacsifier --count --queryfile /base/my_query.csv \
			--config /base/my_config.json --out_directory /base/my_output_dir
