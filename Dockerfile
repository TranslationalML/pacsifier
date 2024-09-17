FROM ubuntu:22.04

WORKDIR /app

###############################################################################
# Update and install necessary system and tool packages
###############################################################################

# Reference to ch.archive.ubuntu.com instead of archive.ubuntu.com 
# RUN sed -i'' 's/archive\.ubuntu\.com/ch\.archive\.ubuntu\.com/' /etc/apt/sources.list

RUN apt-get -y update && apt-get -qq -y install curl dcmtk=3.6.6-5 bzip2 && \
    apt-get autoremove -y --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

###############################################################################
# Install Miniconda3 and set up conda environment
###############################################################################

# Set conda to the $PATH environment variable
ENV PATH /opt/conda/bin:$PATH

# Install conda and create the conda environment
RUN mkdir -p /opt/conda && \
    curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -bfp /opt/conda && \
    rm -rf /tmp/miniconda.sh && \
    conda update -n base -c defaults conda && \
    conda config --add channels conda-forge && \
    conda clean --all --yes

###############################################################################
# Create conda environment from environment file
###############################################################################

# Copy the conda environment file to the image
COPY ./environment/environment_minimal_202401.yml .

# Install the environment
RUN conda env create -f environment_minimal_202401.yml && \
    rm environment_minimal_202401.yml

###############################################################################
# Install PACSIFIER
###############################################################################

WORKDIR /app/pacsifier

# Copy necessary contents of this repository.
COPY ./.coveragerc ./.coveragerc
COPY ./.pytest.ini ./.pytest.ini
COPY setup.py ./setup.py
COPY setup.cfg ./setup.cfg
COPY README.md ./README.md
# COPY LICENSE ./LICENSE
COPY pacsifier ./pacsifier

# Install pacsifier with static version taken from the argument
ARG VERSION=unknown
RUN echo "${VERSION}" > /app/pacsifier/pacsifier/VERSION \
    && conda run -n pacsifier_minimal pip install -e ".[all]" \
    && conda run -n pacsifier_minimal pip install pytest-order

###############################################################################
# Create initial folders for testing / code coverage with correct permissions
###############################################################################

# Create directories for reporting tests and code coverage
# with correct permissions
RUN mkdir -p "/tests/report" && chmod -R 775 "/tests"

# Create directory for storing DICOM files (SCU_STORE) with correct permissions
RUN mkdir -p "/tmp/SCU_STORE" && chmod -R 775 "/tmp/SCU_STORE"
RUN mkdir -p "/tmp/SCU_UPLOAD_STORE" && chmod -R 775 "/tmp/SCU_UPLOAD_STORE"

# Create directory for pytest cache with correct permissions
RUN mkdir -p "/app/pacsifier/.pytest_cache" && chmod -R 775 "/app/pacsifier/.pytest_cache"

###############################################################################
# Set environment variables
###############################################################################

# Tell QT to use the offscreen platform
# ENV QT_QPA_PLATFORM offscreen

# Set the environment variable for .coverage file
ENV COVERAGE_FILE="/tests/report/.coverage"

###############################################################################
# Configure the entrypoint scripts
###############################################################################

# Copy the main entrypoint script 
COPY scripts/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the pytest entrypoint script and make it executable
COPY scripts/docker/entrypoint_pytest.sh /entrypoint_pytest.sh
RUN chmod +x /entrypoint_pytest.sh

# Set the entrypoint to the main entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

###############################################################################
# Container Image Metadata (label schema: http://label-schema.org/rc1/)
###############################################################################

ARG BUILD_DATE=today
ARG VCS_REF=unknown

LABEL org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="PACSIFIER" \
    org.label-schema.description="PACSIFIER: batch DICOM query/retrieve tool for PACS systems" \
    org.label-schema.url="https://translationalml.github.io/" \
    org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.vcs-url="https://github.com/TranslationalML/pacsifier" \
    org.label-schema.version=${VERSION} \
    org.label-schema.maintainer="The TranslationalML team" \
    org.label-schema.vendor="The TranslationalML team" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.docker.cmd="docker run --rm --net=host \
        -v "/path/to/config.json":/config.json \
        -v "/path/to/query.csv":/query.csv \
        -v "/path/to/output/directory":/output \
        pacsifier:1.0.0 \
        pacsifier -c /config.json -i -q /query.csv -d /output" \
    org.label-schema.docker.cmd.test="docker run --rm --net=host \
        --entrypoint /entrypoint_pytest.sh \
        -v /path/to/PACSIFIER/tests:/test \
        -t pacsifier:1.0.0 \
        /test"
