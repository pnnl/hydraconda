#!/bin/bash
set -e
#REM 'estcp' is a variable. TODO
conda env update --name=base
cd project
conda devenv
conda run -n estcp-project invoke project.setup $@
cd ..
