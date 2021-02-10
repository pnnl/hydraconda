@echo on


call            python project_name.py || goto :error
for /f %%i in ('python project_name.py') do set PROJECT_NAME=%%i
set PROJECT_ENV=%PROJECT_NAME%-project

call conda env update --name=base || goto :error
call cd project || goto :error
call conda devenv || goto :error
call conda run -n %PROJECT_ENV% --live-stream invoke work-dir.action.create-scripts-wrappers || goto :error
call copy /Y wbin\project-run-in.bat wbin\_project-run-in.bat || goto :error
call wbin\_project-run-in invoke work-on --work-dir=project || goto :error
call cd .. || goto :error
goto :EOF

:error
exit /b %errorlevel%"
