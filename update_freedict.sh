#!/bin/bash

#$1 abs_path_to_fd_files e.g. '/home/me/repositories/freedict/fd-data'

#if dir exists
if [ -d "${1}" ]; then
  #if empty
  if [ -z "$(ls -A ${1})" ]; then
    python update_freedict.py ${1} --init
  else
    python update_freedict.py ${1}
  fi
else
  #if dir does not exists
  mkdir -p ${1}
  python update_freedict.py ${1} --init
fi
