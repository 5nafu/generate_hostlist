#!/bin/bash

if ! hash virtualenv 2>/dev/null; then
    echo "virtualenv not found. Please install manually"
    exit 1
fi

if [[ -d venv ]] ;  then  
    source ./venv/bin/activate; 
else 
    virtualenv venv && source ./venv/bin/activate; 
fi

pip install --upgrade pybuilder

echo ""
echo "####################################"
echo "####################################"
echo "##                                ##"
echo "##   All dependencies installed   ##"
echo "## To activate the virtualenv run ##"
echo "##                                ##"
echo "##   source ./venv/bin/activate   ##"
echo "##                                ##"
echo "####################################"
echo "####################################"

