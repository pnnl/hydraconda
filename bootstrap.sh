#!/bin/bash
set -e

PROJECT_NAME=$(python project_name.py)
PROJECT_ENV=${PROJECT_NAME}-project

conda env update --name=base
cd project
conda devenv
conda run -n ${PROJECT_ENV} invoke work-dir.action.create-scripts-wrappers
# overwrites
cp wbin/project-run-in wbin/_project-run-in # run-in might get altered during the setup
wbin/_project-run-in invoke work-on --work-dir=project 
cd ..
