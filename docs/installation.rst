.. _installation:

***********************************
Installation Instructions for Users
***********************************


Prerequisites
==============

Docker
------

Ensure that Docker is installed on your system. Docker allows PACSIFIER to run in a containerized environment, simplifying the setup and deployment. Follow the appropriate installation guide for your operating system:

* **Linux**: Follow the official Docker installation guide.
* **Windows (Recommended: WSL)**: Install Docker Desktop for Windows and enable WSL 2 integration. Follow the Docker Desktop installation guide. Make sure to enable the "Use the WSL 2 based engine" option during installation.
* **macOS**: Follow the Docker Desktop installation guide.

* Set Docker to be managed as a non-root user

  * Open a terminal

  * Create the docker group::

    $ sudo groupadd docker

  * Add the current user to the docker group::

    $ sudo usermod -G docker -a $USER

  * Reboot

    After reboot, test if docker is managed as non-root::

      $ docker run hello-world

After installation, verify that Docker is correctly installed by running:

.. code-block:: bash

    docker --version

DCMTK
-----

DCMTK (DICOM Toolkit) is required for interacting with DICOM servers. You can install it as follows:

* **Linux (Ubuntu-based systems)**:

  .. code-block:: bash

      sudo apt install dcmtk

* **Windows (With WSL)**: Follow the same instructions as above within your WSL environment.

For more details about the DCMTK toolkit and available tools, refer to the `DCMTK tools documentation <https://dicom.offis.de/en/dcmtk/dcmtk-tools/>`_.

.. _manual-build-docker-image:

Building the Docker Image
=========================

The Docker image can be built from the Makefile provided in the `PACSIFIER` repository as follows:

.. code-block:: bash

    $ # Clone locally the PACSIFIER repository
    $ git clone https://github.com/TranslationalML/pacsifier.git pacsifier
    $ # Go to the pacsifier directory
    $ cd pacsifier
    $ # Build the docker image
    $ make -B build-docker

You can then inspect the Docker image version tag with the following command:

.. code-block:: bash

    $ docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    pacsifier          <version>           0e0b0b0b0b0b        1 minute ago        1.74GB

Once you know the image tag, you can test the built image by running the command which returns the version installed in the Docker image as follows:

.. code-block:: bash

    $ docker run -it --rm \
        pacsifier:<version> \
        --version

We refer to :ref:`cmdusage-docker` for more details on how to run the Docker image.

Installation from Source (For Developers)
=========================================

If you need to develop or customize PACSIFIER, you can install it from source:

1. **Create a Python Environment:**

   Use Miniconda or another virtual environment manager to create a clean Python environment:

   .. code-block:: bash

      conda create -n pacsifier_minimal python=3.10
      conda activate pacsifier_minimal

2. **Install PACSIFIER:**

   With the environment activated, run:

   .. code-block:: bash

      pip install -e .

   This will install PACSIFIER in editable mode, allowing you to make and test changes easily.

3. **Optional: Install Additional Development Tools**

   If you plan to work on documentation or run tests, you may want to install additional dependencies:

   .. code-block:: bash

      pip install ".[dev,docs,test]"

4. **Verify the Installation:**

   To ensure everything is set up correctly, you can run:

   .. code-block:: bash

      pacsifier --help

   This should display the help message for PACSIFIER, confirming the installation was successful.
