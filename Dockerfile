# build with docker build --network=host -t pacsmanlite . 
FROM ubuntu:16.04
MAINTAINER Jonas Richiardi <jonas.richiardi@chuv.ch>

# install dcmtk and wget 
RUN sed -i'' 's/archive\.ubuntu\.com/ch\.archive\.ubuntu\.com/' /etc/apt/sources.list && \
	apt-get -y update && \
	apt-get -qq -y --no-install-recommends install wget dcmtk bzip2  && \
	apt-get clean autoclean && apt-get autoremove --yes && \
	rm -rf /var/lib/{apt,dpkg,cache,log}/

# install conda and setup env 
RUN wget --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
	/bin/bash /tmp/miniconda.sh -b -f -p /opt/conda && \
	rm -rf /tmp/miniconda.sh && \
	ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
	echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
	echo "conda activate pacsman_minimal" >> ~/.bashrc
# add both conda env and base env
ENV PATH /opt/conda/envs/pacsman_minimal/bin:/opt/conda/bin:$PATH

# create conda env for pacsman - for some reason adding on same line with && causes setup failure - shell issue?
ADD ./files/environment_minimal.yml /tmp/environment_minimal.yml
RUN conda update conda
RUN conda env create -n pacsman_minimal -f /tmp/environment_minimal.yml
RUN conda clean --all --yes

ENTRYPOINT ["python", "/app/code/pacsman.py"]

WORKDIR /app

COPY . /app
