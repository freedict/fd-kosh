#!/bin/bash

#$1 abs_path_to_fd_files e.g. '/home/me/repositories/freedict/fd-data'
#$2 abs_path to conda.sh e.g. '/home/me/miniconda3/etc/profile.d/conda.sh'

source ${2}
conda activate freedict

if [ ! -d "${1}" ]; then
  # if the path does not exist, create it and download all dicts from freedict.org
  mkdir -p ${1}
  python update_freedict.py ${1} --init
else
  # update the files
  python update_freedict.py ${1}
fi
