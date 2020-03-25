#!/bin/bash

# $1 path to (compressed) freedicts
# $2 path where they should be unpacked

for dir in ${1}*;
do
  if [ -d "$dir" ]; then
    cd ${dir}
    dir_id=`basename "${dir}"`
    last=$(ls -v | tail -1)
    if [ -d "$last" ]; then
      cd $last
      src=$(find . -name "*.src.tar.xz" -printf "%f\n"| head -n 1)
      echo $src
      mkdir -p ${2}
      echo "${dest} created"
      echo "1 ${dir}/${last}/${src}"
      echo "2 ${dest}/${src}"
      cp ${dir}/${last}/${src} ${2}${src}
      #decompress
      cd ${2}
      tar -xf ${2}${src}
      #remove tar.xz file
      rm ${2}${src}
    fi
  fi
done
