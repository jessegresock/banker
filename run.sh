#!/bin/bash

set -e

if [[ $# -eq 0 ]]
then
    flask --app manage run --debug
fi

flask --app manage run