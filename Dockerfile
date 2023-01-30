FROM ubuntu:18.04
MAINTAINER Jonas Richiardi <jonas.richiardi@chuv.ch>
RUN sed -i'' 's/archive\.ubuntu\.com/ch\.archive\.ubuntu\.com/' /etc/apt/sources.list

# update necessary system packages, install conda
RUN apt-get -y update && apt-get -qq -y install curl dcmtk bzip2
RUN curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && bash /tmp/miniconda.sh -bfp /opt/conda && rm -rf /tmp/miniconda.sh

# set up conda environment
ENV PATH /opt/conda/bin:$PATH
RUN conda update -n base -c defaults conda && conda config --add channels conda-forge
COPY ./deployment/utils/environment_minimal_202301.yml .
RUN conda env create -f environment_minimal_202301.yml
RUN conda clean --all --yes

WORKDIR /app

COPY . /app

ENTRYPOINT ["conda", "run", "-n", "pacsman_minimal", "python", "/app/pacsman.py"]

