#!/bin/bash

#disable the "errexit" option, even if a command within the script fails,
#the script will continue executing the subsequent commands instead of immediately terminating.
set +e

#change the pipeline behaviour
set -o pipeline

global_status=0

echo -e "#### RUNNING docstring completeness test ####\n"

uv run interrogate -v llm_pyexecutor
status=$?

if [[ status -eq 0 ]]
then 
    echo -e "\n#### SUCCESS: docstring completeness passed. ####\n"
else
    echo -e "\n#### FAILURE: docstring completeness failed. ####\n"
    global_status=1
fi
