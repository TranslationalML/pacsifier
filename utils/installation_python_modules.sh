#!/bin/bash
miniconda_root="/home/localadmin/anaconda2"

DIR=`dirname "$0"`
PACSMANDIR=`dirname "$DIR"`

echo $PACSMANDIR

#Launch our miniconda3 environment with all dependencies installed, except heudiconv and dcmstack
echo "Activate conda environment heudiconvquery"
source "${miniconda_root}/bin/activate" heudiconvquery

#Installation of Heudiconv
echo "Installation of Heudiconv"
cd ${PACSMANDIR}/heudiconv
pip install .[all]

#Installation of dcmstack (specific version compatible with python3 (https://github.com/mvdoc/dcmstack.git)
#The one provided by conda is only python2 compatible)
echo "Installation of dcmstack"
cd ${PACSMANDIR}/dcmstack
python setup.py install

#echo "Deactivate conda environment heudiconvquery"
source "${miniconda_root}/bin/deactivate" heudiconvquery
