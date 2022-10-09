#!/bin/bash

set -e

SCRIPT_DIR=$(realpath $(dirname ${BASH_SOURCE[0]}))

build_one()
{
    lambda_package=$1
    [ -d $lambda_package ] && lambda_package=$(basename $1)   
    dir="$SCRIPT_DIR/$lambda_package" 
    [ ! -d $dir ] && ( echo "$dir doesn't exist. Abort" && return 1 )
    echo "Start building ${dir##*/}"
    pushd $dir
    mkdir $dir/third_party
    lambda_name="$(basename -- $dir)"
    touch $dir/requirements.txt
    pip install -r $dir/requirements.txt --target $dir/third_party
    cp lambda_function.py $dir/third_party/
    cd $dir/third_party
    zip -r $SCRIPT_DIR/$lambda_name.zip .
    popd
    rm -r $dir/third_party
    echo "Done building ${dir##*/}" 
}

if [[ -z $1 ]]; then
  echo 'first arg is empty, you should specify `--all` or `$lambda_sevice_folder`. Abort'
  exit 1
else
  echo "Start to build single lambda package $1"
  build_one $1
  echo "Done building single lambda package $1"
fi
