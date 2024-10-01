@echo off
setlocal enabledelayedexpansion

REM スクリプトが存在するディレクトリの絶対パスを取得
set BASEDIR=%~dp0

REM コマンドライン引数の処理
if "%1" == "create-def" (
    shift
    call :CreateDef %*
    goto :eof
) else if "%1" == "cli" (
    call :Cli
    goto :eof
) else if "%1" == "-help" (
    echo Usage:
    echo   fountain-flow cli - Launch CLI.
    echo   fountain-flow create-def [ddl paths...] - Execute DDL scripts to create definitions
    echo   fountain-flow -help - Display this help message
    goto :eof
) else (
    echo Error: Invalid command or arguments
    echo Try 'fountain-flow -help' for more information.
    goto :eof
)

REM 関数の定義
:CreateDef
    set abs_paths=
    for %%i in (%*) do (
        REM 各相対パスを絶対パスに変換
        for /f "delims=" %%a in ('powershell -command "[System.IO.Path]::GetFullPath('%%i')"') do (
            set abs_paths=!abs_paths! %%a
        )
    )
    REM 絶対パスをPythonスクリプトに渡す
    python "%BASEDIR%..\tools\create-def\app.py" %abs_paths%
    goto :eof

:Cli
    python "%BASEDIR%..\src\cli.py"
    goto :eof

endlocal