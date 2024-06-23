@echo off
setlocal

REM スクリプトが存在するディレクトリの絶対パスを取得
set BASEDIR=%~dp0

REM Function definitions
:run_app
python "%BASEDIR%..\src\app.py" %*
goto :eof

:create_def
shift
REM Create an array to hold the absolute paths
setlocal enabledelayedexpansion
set abs_paths=
for %%I in (%*) do (
    for /f "delims=" %%A in ('powershell -command "(Resolve-Path %%I).Path"') do (
        set abs_paths=!abs_paths! "%%A"
    )
)
REM Pass the absolute paths to the Python script
python "%BASEDIR%..\tools\create-def\app.py" %abs_paths%
endlocal
goto :eof

REM Command line handling
if "%1"=="run" (
    shift
    call :run_app %*
) else if "%1"=="create-def" (
    shift
    call :create_def %*
) else if "%1"=="show-def" (
    call :show_def
) else if "%1"=="-help" (
    echo Usage:
    echo   fountain-flow run [--env [environment]] - Run the main application optionally in a specified environment
    echo   fountain-flow create-def [ddl paths...] - Execute DDL scripts to create definitions
    echo   fountain-flow -help - Display this help message
) else (
    echo Error: Invalid command or arguments
    echo Try 'fountain-flow -help' for more information.
)

endlocal