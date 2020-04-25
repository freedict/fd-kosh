#!/bin/bash

# $1 base dir to freedict data (/var/www)
# $2 path where they should be unpacked (/home/me/fd-data)

#up_to_date_db="${1}/freedict-database.json"

#if dir exists
if [ -d "${2}" ]; then
  #if empty
  if [ -z "$(ls -A ${2})" ]; then
    python3 update_freedict.py ${1} ${2} --init
  else
    python3 update_freedict.py ${1} ${2}
  fi
else
  #if dir does not exist
  mkdir -p ${2}
  python3 update_freedict.py ${1} ${2} --init
fi
