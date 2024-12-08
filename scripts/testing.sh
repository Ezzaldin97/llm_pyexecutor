#!/bin/bash

#disable the "errexit" option, even if a command within the script fails,
#the script will continue executing the subsequent commands instead of immediately terminating.
set +e

#change the pipeline behaviour
set -o pipeline

global_status=0

echo -e "#### RUNNING unit-testing ####\n"
uv run pytest -v .
status=$?

if [[ status -eq 0 ]]
then 
    echo -e "\n#### SUCCESS: unit-testing passed. ####\n"
else
    echo -e "\n#### FAILURE: unit-testing failed. ####\n"
    global_status=1
fi

if [[ -d "tests/local_executor" ]]
then
    rm -rf tests/local_executor
    echo "executor DIR removed"
fi
