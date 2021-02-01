@echo on


for /f %%i in ('python project_name.py') do set PROJECT_NAME=%%i
set PROJECT_ENV=%PROJECT_NAME%-project

conda env update --name=base &&^
cd project &&^
conda devenv &&^
conda run -n %PROJECT_ENV% invoke work-dir.action.create-scripts-wrappers &&^
copy /Y wbin\project-run-in.bat wbin\_project-run-in.bat &&^
wbin\_project-run-in invoke work-on --work-dir=project --no-skip-project-workdir &&^
cd ..
