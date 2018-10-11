FROM ubuntu:16.04
MAINTAINER Firas BEN OTHMAN <firas.benothman@epfl.ch>
RUN sed -i'' 's/archive\.ubuntu\.com/ch\.archive\.ubuntu\.com/' /etc/apt/sources.list

RUN apt-get -y update && apt-get -qq -y install curl dcmtk bzip2
RUN curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh &&     bash /tmp/miniconda.sh -bfp /opt/conda &&     rm -rf /tmp/miniconda.sh

ENV PATH /opt/conda/bin:$PATH

RUN conda install -y python=3.5.5 &&     conda update conda &&     conda clean --all --yes
RUN conda config --add channels conda-forge

RUN pip install ordereddict==1.1
RUN pip install inotify==0.2.10
RUN conda install -c conda-forge pyqt=4
RUN conda install -c conda-forge tqdm=4.25.0
RUN conda install -c conda-forge py=1.6.0
RUN conda install -c conda-forge pytest=3.7.4
RUN conda install -c conda-forge pandas=0.23.4
RUN conda install -c conda-forge datalad=0.10.2
RUN conda install -c conda-forge chardet=3.0.4
RUN conda install -c conda-forge nipype=1.1.0
RUN conda install -c conda-forge six=1.11.0
RUN conda install -c conda-forge setuptools=40.2.0
RUN conda install -c conda-forge hypothesis=3.71.3
RUN conda install -c conda-forge numpy=1.15.1
RUN conda install -c conda-forge nose=1.3.7
RUN conda install -c conda-forge nibabel=2.3.0
RUN conda install -c conda-forge mock=2.0.0
RUN conda install -c conda-forge Cerberus=1.2
RUN conda install -c conda-forge tinydb=3.11.0
RUN conda install -c conda-forge pydicom=0.9.9
RUN conda install -c conda-forge typing=3.6.6

RUN conda clean --all --yes

ENTRYPOINT ["python", "/app/code/pacsman.py"]

WORKDIR /app

COPY . /app
