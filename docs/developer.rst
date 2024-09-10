.. _instructions:

***************************
Instructions for Developers
***************************


.. _instructions_docker_build:

How to build the Docker image locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to the clone directory of your fork and run the following command in the terminal ::

    cd pacsman
    make -B build-docker

.. note::
    The tag of the version of the image is generated from the git tag thanks to the versioneer.py library.


.. _instructions_pacsman_install:

How to install `PACSMAN` locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. PACSMAN relies on the `DCMTK`_ tools for DICOM network communication. It can be easily installed on Ubuntu with the following command:

    .. code-block:: bash

        apt-get install dcmtk

    For other operating systems, please refer to the DCMTK_ documentation.

2. Install the Python environment with `PACSMAN` and its dependencies.

2.1 It is recommended to use a virtual environment to install `PACSMAN` and its dependencies, which can be achieved using `venv`_ or `conda`_. For convenience, a minimal `conda` environment is provided in the `environment` directory of the repository. It can be installed as follow:

    .. code-block:: bash

        conda create env -f environment/environment_minimal_202301.yml
        conda activate pacsman_minimal

    If you prefer to use `venv`, you can create a virtual environment and activate it as follow::

        python3 -m venv venv
        source venv/bin/activate            

.. important::
    `PACSMAN` requires a Python environment with `python>=3.10`.

2.2 Once the virtual environment is activated, `PACSMAN` can be installed with the following command:

2. Install `PACSMAN` along with all its Python dependencies (including dependencies to build the documentation and to test the package)::

    pip install -e .[all]

   or ::

    pip install -e .\[all\]


.. _instructions_docs_build:

How to build the documentation locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to the cloned repository and run the following `make` command::

    make -B build-docs

This will re-install PACSMAN's python package, clean any existing documentation, and build the documentation in the `docs/build/html` directory.

The built HTML files of the documentation, including its main page (``index.html``), can be found in the ``docs/_build/html`` directory, and can be opened in your favorite browser.


.. _instructions_testing:

How to Test PACSMAN
~~~~~~~~~~~~~~~~~~~~
To make sure PACSMAN works smoothly after your changes, you can run a series of automated tests. Here are the steps to run these tests using either Docker or your local setup.


.. _instructions_tests:

**Run the tests via the Docker image**

1. Go to the clone directory of your fork and (re-)build the Docker image with the following commands::

    make -B build-docker

2. Run the tests throughout the Docker image::

    make test


.. _instructions_tests_local:

**Run the tests locally**

Before running the tests locally, you need to set up a mock server to simulate a DICOM network service. While this documentation details instructions for using `dcmqrscp`, which is included in the DCMTK tools, it is also possible to use other tools to achieve similar functionality. Setting up a mock server allows you to verify the functionality of PACSMAN without requiring a real DICOM server.

1. **Start the mock server**: Open a separate terminal and navigate to the `tests` directory. Then run the following command:

    .. code-block:: bash

        cd tests
        dcmqrscp -v -c ./config/dcmqrscp.cfg

2. **Check connection**: To ensure the connection to the mock server is successful, run the following command in another terminal:

    .. code-block:: bash

        echoscu -ll trace -aec SCU_STORE -aet PACSIFIER_CLIENT localhost 4444
    
    If the connection does not work, try restarting the mock server and then checking the connection again.

3. **Run the tests**: Now that the mock server is running, you can run the tests locally. Go to the cloned repository folder and (re-)install `PACSMAN` and its dependencies (see :ref:`instructions_pacsman_install`).

4. To run the tests, use the following command::

    pytest ./tests

.. tip:: 
      If you want to generate a coverage report, you can run the tests with the following command::

        pytest --cov=pacsman --cov-report html ./tests

.. _tests_outputs:

**Outputs of tests**

In both cases, the tests are run in a temporary `tmp` directory in the `tests` directory, so that the original data are not modified. After completion, coverage report in HTML format can be found in ``htmlcov`` folder and can be displayed by opening ``index.html`` in your favorite browser.


.. _venv: https://docs.python.org/3/library/venv.html
.. _conda: https://docs.conda.io/en/latest/
.. _DCMTK: https://dicom.offis.de/en/dcmtk/