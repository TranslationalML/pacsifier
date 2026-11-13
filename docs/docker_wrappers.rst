.. _docker_wrappers:

******************
Docker Wrappers
******************

Overview
========

The PACSIFIER package includes convenient Docker wrapper scripts that allow users to run CLI commands via Docker without needing to remember complex ``docker run`` command syntax. These wrappers handle volume mounting and Docker configuration automatically.

Available Wrapper Scripts
=========================

The following Docker wrapper scripts are available:

* ``docker_pacsifier``: Docker wrapper for the main ``pacsifier`` command
* ``docker_get_pseudonyms``: Docker wrapper for ``pacsifier-get-pseudonyms``
* ``docker_add_karnak_tags``: Docker wrapper for ``pacsifier-add-karnak-tags``
* ``docker_anonymize_dicoms``: Docker wrapper for ``pacsifier-anonymize``
* ``docker_extract_carestream_report``: Docker wrapper for ``pacsifier-extract-carestream-report``
* ``docker_move_dumps``: Docker wrapper for ``pacsifier-move-csv``
* ``docker_create_dicomdir``: Docker wrapper for ``pacsifier-create-dicomdir``

Configuration
=============

Docker Image Selection
----------------------

By default, the wrapper scripts use the ``pacsifier:latest`` Docker image. You can override this in two ways:

1. Set the ``PACSIFIER_DOCKER_IMAGE`` environment variable:

.. code-block:: bash

   export PACSIFIER_DOCKER_IMAGE=pacsifier:X.Y.Z

2. Use the ``--image`` flag with each command:

.. code-block:: bash

   docker_pacsifier --image pacsifier:X.Y.Z -c config.json -i -q query.csv -d /output --save

Usage Examples
==============

docker_pacsifier
----------------

Run the main PACSIFIER command:

.. code-block:: bash

   docker_pacsifier -c config.json -i -s -q query.csv -d /output

Resume an interrupted extraction:

.. code-block:: bash

   docker_pacsifier -c config.json -q query.csv -d /output --save --resume

docker_get_pseudonyms
---------------------

Get pseudonyms for DICOM data:

.. code-block:: bash

   docker_get_pseudonyms --mode de-id -c config.json -q query.csv -a ProjectName -d /output

docker_add_karnak_tags
----------------------

Add Karnak tags to DICOM files:

.. code-block:: bash

   docker_add_karnak_tags -d /path/to/input -n /path/to/new_ids.json -a AlbumName

docker_anonymize_dicoms
-----------------------

Anonymize DICOM files:

.. code-block:: bash

   docker_anonymize_dicoms -d /path/to/input -o /path/to/output -i -p -a

docker_extract_carestream_report
--------------------------------

Extract Carestream reports:

.. code-block:: bash

   docker_extract_carestream_report -d /path/to/data

docker_move_dumps
-----------------

Move CSV dump files:

.. code-block:: bash

   docker_move_dumps -d /path/to/dicom -o /path/to/info

docker_create_dicomdir
----------------------

Create a DICOMDIR file:

.. code-block:: bash

   docker_create_dicomdir -d /path/to/input -o /path/to/output

How It Works
============

Volume Mounting
---------------

The wrapper scripts automatically handle Docker volume mounting. When you provide file or directory paths as arguments, the scripts:

1. Convert the paths to absolute paths
2. Mount them as Docker volumes at standardized container paths
3. Pass the container paths to the PACSIFIER CLI commands

For example, when you run:

.. code-block:: bash

   docker_pacsifier -c /home/user/config.json -q /home/user/query.csv -d /home/user/output --save

The wrapper script:

1. Mounts ``/home/user/config.json`` as ``/config.json`` in the container
2. Mounts ``/home/user/query.csv`` as ``/query.csv`` in the container
3. Mounts ``/home/user/output`` as ``/output`` in the container
4. Runs ``pacsifier -c /config.json -q /query.csv -d /output --save`` inside the container

Network Configuration
---------------------

By default, the wrapper scripts use ``--net=host`` to allow the containerized PACSIFIER to communicate with PACS servers on the host network.

User Configuration
------------------

The Docker image runs as a non-root user. To let the container write to the mounted
directories, the Python wrappers (``docker_*`` commands) run it with your own
UID and GID (``--user <uid>:<gid>``), so output files are owned by you.
On platforms without UIDs (e.g. Windows), no ``--user`` option is passed.

To use a different user, set the ``PACSIFIER_DOCKER_USER`` environment variable
(an empty value keeps the image's default user):

.. code-block:: bash

   export PACSIFIER_DOCKER_USER=1000:1000
   docker_pacsifier -c config.json -q query.csv -d /output --save

Troubleshooting
===============

Docker Not Found
----------------

If you see an error message stating "Docker not found", ensure that:

1. Docker is installed on your system
2. Docker is in your system PATH
3. You have the necessary permissions to run Docker commands

Image Not Found
---------------

If the Docker image is not found, you may need to:

1. Build the PACSIFIER Docker image first
2. Specify the correct image name using the ``--image`` flag or ``PACSIFIER_DOCKER_IMAGE`` environment variable

See Also
========

* :ref:`cmdusage` - Command-line usage documentation
* :ref:`installation` - Installation instructions including Docker setup
