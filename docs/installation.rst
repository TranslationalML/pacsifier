.. _installation:

***********************************
Installation Instructions
***********************************

PACSIFIER can be installed in several ways, ordered from simplest to most flexible:

1. :ref:`install-docker-pull` — Pre-built Docker image from Quay.io *(recommended for most users)*
2. :ref:`install-pip` — Install via ``pip`` from PyPI
3. :ref:`install-docker-build` — Build the Docker image locally
4. :ref:`install-source` — Install from source *(for developers)*


.. _install-docker-pull:

Option 1: Pre-built Docker Image (Recommended)
===============================================

The simplest way to use PACSIFIER. No need to clone the repository or install any dependencies — everything is bundled in the Docker image.

Prerequisites
-------------

Ensure Docker is installed on your system:

* **Linux**: Follow the `official Docker installation guide <https://docs.docker.com/engine/install/ubuntu/>`_.
* **Windows (Recommended: WSL)**: Install Docker Desktop for Windows and enable WSL 2 integration. Follow the `Docker Desktop installation guide <https://docs.docker.com/desktop/install/windows-install/>`_.
* **macOS**: Follow the `Docker Desktop installation guide <https://docs.docker.com/desktop/install/mac-install/>`_.

On Linux, set Docker to be managed as a non-root user:

.. code-block:: bash

    sudo groupadd docker
    sudo usermod -G docker -a $USER
    # Reboot, then verify:
    docker run hello-world

Pull and Run
------------

Pull the latest release image from Quay.io:

.. code-block:: bash

    docker pull quay.io/translationalml/pacsifier:latest

Test that it works:

.. code-block:: bash

    docker run --rm quay.io/translationalml/pacsifier:latest pacsifier --version

Run a query:

.. code-block:: bash

    docker run --rm --net=host --user "$(id -u):$(id -g)" \
        -v /path/to/my_dir:/base \
        quay.io/translationalml/pacsifier:latest \
        pacsifier --save --info --queryfile /base/my_query.csv \
            --config /base/my_config.json --out_directory /base/my_output_dir

.. note::
    The image runs as a non-root user. ``--user "$(id -u):$(id -g)"`` makes the container
    run as your own user so that it can write to the mounted directories
    and the output files are owned by you.

.. tip::
    You can pin to a specific version instead of ``latest`` (e.g., ``quay.io/translationalml/pacsifier:1.0.0``).
    See `available tags on Quay.io <https://quay.io/repository/translationalml/pacsifier?tab=tags>`_.

.. note::
    DCMTK and all other dependencies are included inside the Docker image.
    You do **not** need to install them separately.

We refer to :ref:`cmdusage-docker` for more details on running the Docker image,
and :ref:`docker_wrappers` for convenience wrapper scripts that simplify the
``docker run`` command syntax.


.. _install-pip:

Option 2: Install via pip
=========================

PACSIFIER is published on `PyPI <https://pypi.org/project/pacsifier/>`_:

.. code-block:: bash

    pip install pacsifier

.. important::
    When installing via pip, you must also install **DCMTK** on your system
    for DICOM network communication:

    * **Linux (Ubuntu-based)**: ``sudo apt install dcmtk``
    * **Windows (WSL)**: Same command within your WSL environment
    * **macOS**: ``brew install dcmtk``

    For more details, see the `DCMTK documentation <https://dicom.offis.de/en/dcmtk/dcmtk-tools/>`_.

Verify the installation:

.. code-block:: bash

    pacsifier --help


.. _install-docker-build:

Option 3: Build Docker Image Locally
=====================================

If you need the latest development version or want to customize the Docker image,
you can build it from the repository:

.. code-block:: bash

    git clone https://github.com/TranslationalML/pacsifier.git
    cd pacsifier
    make build-docker

Inspect the built image:

.. code-block:: bash

    docker images | grep pacsifier

Test the image:

.. code-block:: bash

    docker run --rm pacsifier:latest pacsifier --version

.. note::
    DCMTK is included inside the Docker image. You do **not** need to install it separately.


.. _install-source:

Option 4: Install from Source (For Developers)
===============================================

For developing or customizing PACSIFIER:

1. **Install DCMTK** (required for DICOM network communication):

   .. code-block:: bash

      sudo apt install dcmtk

   For other operating systems, see the `DCMTK documentation <https://dicom.offis.de/en/dcmtk/dcmtk-tools/>`_.

2. **Clone the repository:**

   .. code-block:: bash

      git clone https://github.com/TranslationalML/pacsifier.git
      cd pacsifier

3. **Create a Python environment** (Python >= 3.11 required):

   Using conda with a manual environment:

   .. code-block:: bash

      conda create -n pacsifier_minimal python=3.12
      conda activate pacsifier_minimal

   Or using the provided environment file:

   .. code-block:: bash

      conda env create -f environment/environment_minimal_202401.yml
      conda activate pacsifier_minimal

   Or using ``venv``:

   .. code-block:: bash

      python3 -m venv venv
      source venv/bin/activate

4. **Install PACSIFIER in editable mode:**

   .. code-block:: bash

      pip install -e .

   For full development (documentation, tests, linting):

   .. code-block:: bash

      pip install -e ".[all]"

5. **Verify the installation:**

   .. code-block:: bash

      pacsifier --help

   This should display the help message for PACSIFIER, confirming the installation was successful.
