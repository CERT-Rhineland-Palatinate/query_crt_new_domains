#!/bin/bash

# Example wrapperscript for running main in an virtualenv from cron

script_path=$(realpath $0)
dir_path=$(dirname $script_path)

cd $dir_path
source bin/activate

./main.py -v -t rlp.de
