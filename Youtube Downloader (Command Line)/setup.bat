@echo off
set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )
title Youtube Downloader (Setup)
SETLOCAL EnableDelayedExpansion
REM Check if Python is installed
py --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading and installing...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
    start /wait "" python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    del python-installer.exe
    echo Python installed.

    REM Wait for py command to become available
    set /a count=0
    :wait_python
    py --version >nul 2>&1
    if ERRORLEVEL 1 (
        timeout /t 2 >nul
        set /a count+=1
        if !count! GEQ 10 (
            echo ERROR: Python did not become available after installation.
            exit /b 1
        )
        goto wait_python
    )
)

REM Upgrade pip
py -m ensurepip --upgrade
py -m pip install --upgrade pip

REM Install required Python packages
py -m pip install pytubefix tqdm

REM Check for ffmpeg
where ffmpeg >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo WARNING: ffmpeg not found. MP3 conversion may fail.
    echo Download ffmpeg manually from https://ffmpeg.org/download.html or install via choco: choco install ffmpeg
)

REM Run youtube_downloader.bat
cls
echo Run start.bat to use
pause
