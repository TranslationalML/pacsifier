.. _instructions:

***************************
Instructions for Developers
***************************


.. _instructions_docker_build:

How to build the Docker image locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the clone directory of your fork and run the following command in the terminal ::

    cd pacsifier
    make -B build-docker

.. note::
    The tag of the version of the image is generated from the git tag thanks to the versioneer.py library.


.. _instructions_pacsifier_install:

How to install `PACSIFIER` locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. PACSIFIER relies on the `DCMTK`_ tools for DICOM network communication. It can be easily installed on Ubuntu with the following command:

    .. code-block:: bash

        apt-get install dcmtk

    For other operating systems, please refer to the DCMTK_ documentation.

2. Install the Python environment with `PACSIFIER` and its dependencies.

2.1 It is recommended to use a virtual environment to install `PACSIFIER` and its dependencies, which can be achieved using `venv`_ or `conda`_. For convenience, a minimal `conda` environment is provided in the `environment` directory of the repository. It can be installed as follow:

    .. code-block:: bash

        conda create env -f environment/environment_minimal_202301.yml
        conda activate pacsifier_minimal

    If you prefer to use `venv`, you can create a virtual environment and activate it as follow::

        python3 -m venv venv
        source venv/bin/activate            

.. important::
    `PACSIFIER` requires a Python environment with `python>=3.10`.

2.2 Once the virtual environment is activated, `PACSIFIER` can be installed with the following command:

2. Install `PACSIFIER` along with all its Python dependencies (including dependencies to build the documentation and to test the package)::

    pip install -e .[all]

   or ::

    pip install -e .\[all\]


.. _instructions_docs_build:

How to build the documentation locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to the cloned repository and run the following `make` command::

    make -B build-docs

This will re-install PACSIFIER's python package, clean any existing documentation, and build the documentation in the `docs/build/html` directory.

The built HTML files of the documentation, including its main page (``index.html``), can be found in the ``docs/_build/html`` directory, and can be opened in your favorite browser.


.. _instructions_tests:

How to run the tests via the Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the clone directory of your fork and (re-)build the Docker image with the following commands::

    make -B build-docker

2. Run the tests throughout the Docker image::

    make test


.. _instructions_tests_local:

How to run the tests locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before running the tests locally, you need to set up a mock server to simulate a DICOM network service. This documentation details instructions for using `dcmqrscp`, included in the DCMTK tools, to verify the functionality of PACSIFIER without requiring a real DICOM server.

1. **Start the mock server**: Open a separate terminal and navigate to the `tests` directory. Then run the following command:

    .. code-block:: bash

        cd tests
        dcmqrscp -v -c ./config/dcmqrscp.cfg

2. **Check connection**: To ensure the connection to the mock server is successful, run the following command in another terminal:

    .. code-block:: bash

        echoscu -ll trace -aec SCU_STORE -aet PACSIFIER_CLIENT localhost 4444

    If the connection does not work, try restarting the mock server and then checking the connection again.

3. **Run the tests**: Now that the mock server is running, you can run the tests locally. Go to the cloned repository folder and (re-)install `PACSIFIER` and its dependencies (see :ref:`instructions_pacsifier_install`).

4. To run the tests, use the following command:

    .. code-block:: bash

        pytest ./tests

.. tip:: 
      If you want to generate a coverage report, you can run the tests with the following command:

      .. code-block:: bash

        pytest --cov=pacsifier --cov-report html ./tests


.. _tests_outputs:

Outputs of tests
~~~~~~~~~~~~~~~~~

In both cases, the tests are run in a temporary `tmp` directory in the `tests` directory, so that the original data are not modified. After completion, coverage report in HTML format can be found in the ``htmlcov`` folder and can be displayed by opening ``index.html`` in your favorite browser.


.. _venv: https://docs.python.org/3/library/venv.html
.. _conda: https://docs.conda.io/en/latest/
.. _DCMTK: https://dicom.offis.de/en/dcmtk/