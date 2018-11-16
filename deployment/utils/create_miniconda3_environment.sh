#!/usr/bin/env sh

DIR=`dirname "$0"`
PACSMANDIR=`dirname "$DIR"`

echo $PACSMANDIR

conda create --name heudiconvquery --list "${PACSMANDIR}/utils/miniconda3_spec_file.txt"
