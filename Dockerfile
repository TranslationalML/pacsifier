# build with docker build --network=host -t pacsmanlite . 
FROM ubuntu:16.04
MAINTAINER Jonas Richiardi <jonas.richiardi@chuv.ch>

RUN sed -i'' 's/archive\.ubuntu\.com/ch\.archive\.ubuntu\.com/' /etc/apt/sources.list && \
	apt-get -y update && \
	apt-get -qq -y --no-install-recommends install wget dcmtk bzip2  && \
	apt-get clean autoclean && apt-get autoremove --yes && \
	rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN wget --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
	/bin/bash /tmp/miniconda.sh -b -f -p /opt/conda && \
	rm -rf /tmp/miniconda.sh
#RUN ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
#	echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
#	echo "conda activate base" >> ~/.bashrc

ENV PATH /opt/conda/bin:$PATH
#ENV CONDAPATH /opt/conda/bin/

#RUN conda update conda && conda install -y python=3.5.5 && conda clean --all --yes && conda config --add channels conda-forge
RUN conda update conda && conda clean --all --yes && conda config --add channels conda-forge
ADD ./files/environment_minimal.yml /tmp/environment_minimal.yml
RUN conda env create -n dicom_project -f /tmp/environment_minimal.yml && conda clean --all --yes

ENTRYPOINT ["python", "/app/code/pacsman.py"]

WORKDIR /app

COPY . /app
