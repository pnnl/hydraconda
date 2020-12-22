@echo on
for /f %%i in ('python project_name.py') do set PROJECT_NAME=%%i
set PROJECT_ENV=%PROJECT_NAME%-project

conda env update --name=base &&^
cd project &&^
conda devenv &&^
conda run -n %PROJECT_ENV% --live-stream invoke project.setup %* &&^
cd ..
