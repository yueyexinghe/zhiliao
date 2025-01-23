@echo off
pushd %~dp0

set _ENV_FOLDER=python-3.10.9-embed-amd64

if exist .\%_ENV_FOLDER%\envinit.bat (
	call .\%_ENV_FOLDER%\envinit.bat
	del .\%_ENV_FOLDER%\envinit.bat
)

call .\%_ENV_FOLDER%\activate.bat

python ZhiliaoClient.pyw

call .\%_ENV_FOLDER%\deactivate.bat
popd
