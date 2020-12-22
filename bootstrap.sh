#!/bin/bash
set -e

PROJECT_NAME=$(python project_name.py)
PROJECT_ENV=${PROJECT_NAME}-project

conda env update --name=base
cd project
conda devenv
conda run -n ${PROJECT_ENV} --live-stream invoke project.setup $@
cd ..
