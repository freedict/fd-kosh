#!/bin/bash

#$1 abs_path_to_fd_files e.g. '/home/me/repositories/freedict/fd-data'

if [ ! -d "${1}" ]; then
  # if the path does not exist, create it and download all dicts from freedict.org
  mkdir -p ${1}
  python update_freedict.py ${1} --init
else
  # update the files
  python update_freedict.py ${1}
fi
