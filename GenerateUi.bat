@echo off
pushd %~dp0\Ui
for /R %%i in (*.ui)do pyuic5 %%~ni.ui -o %%~ni.py
for /R %%i in (*.qrc)do pyrcc5 %%~ni.qrc -o ..\%%~ni_rc.py
popd

