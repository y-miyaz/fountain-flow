@echo off
setlocal EnableDelayedExpansion

REM スクリプトが存在するディレクトリの絶対パスを取得
set BASEDIR=%~dp0

REM Function to create definitions
:CREATE_DEF
shift
set ABS_PATHS=
:LOOP
if "%~1"=="" goto END_LOOP
for %%i in ("%~1") do (
    set ABS_PATHS=!ABS_PATHS! "%%~fi"
)
shift
goto LOOP
:END_LOOP
python "%BASEDIR%..\tools\create-def\app.py" %ABS_PATHS%
goto :EOF

REM Function to launch CLI
:CLI
python "%BASEDIR%..\src\cli.py"
goto :EOF

REM Command line handling
if "%1"=="create-def" (
    call :CREATE_DEF %*
) else if "%1"=="cli" (
    call :CLI
) else if "%1"=="-help" (
    echo Usage:
    echo   fountain-flow cli - Launch CLI.
    echo   fountain-flow create-def [ddl paths...] - Execute DDL scripts to create definitions
    echo   fountain-flow -help - Display this help message
) else (
    echo Error: Invalid command or arguments
    echo Try 'fountain-flow -help' for more information.
)
