@echo off
setlocal
set "CONNECT_ENTRY=%~dp0workbench.py"
set "CONNECT_ARGS="
if /I "%~1"=="--cli" (
    set "CONNECT_ENTRY=%~dp0connect.py"
    set "CONNECT_ARGS=menu"
)
if not defined CONNECT_MTK_REPO if exist "%~dp0vendor\mtkclient" set "CONNECT_MTK_REPO=%~dp0vendor\mtkclient"
set "CONNECT_PYTHON=%~dp0.venv\Scripts\python.exe"
if exist "%CONNECT_PYTHON%" (
    "%CONNECT_PYTHON%" -X utf8 "%CONNECT_ENTRY%" %CONNECT_ARGS%
) else (
    py -3 -X utf8 "%CONNECT_ENTRY%" %CONNECT_ARGS%
)
if errorlevel 1 pause
