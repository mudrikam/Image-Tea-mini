@echo off
setlocal enabledelayedexpansion

REM =====================================================================
REM Image Tea Mini Launcher Script
REM Author: Mudrikul Hikam
REM Last Updated: May 13, 2025
REM 
REM This script performs the following tasks:
REM 1. If Python folder exists, directly runs main.py
REM 2. If Python folder doesn't exist:
REM    - Downloads Python 3.12.10 embedded distribution
REM    - Sets up pip in the embedded distribution
REM    - Updates application files from GitHub repository
REM    - Installs required packages from requirements.txt
REM    - Runs main.py
REM =====================================================================

REM Set base directory to the location of this batch file (removes trailing backslash)
set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
set "PYTHON_DIR=%BASE_DIR%\python\Windows"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "MAIN_PY=%BASE_DIR%\main.py"

REM =====================================================================
REM Check if Python directory exists
REM If it exists, we can directly run the main.py file without setup
REM If not, we need to set up the environment first
REM =====================================================================
if exist "%PYTHON_DIR%" (
    echo Python installation found. Checking requirements...
    
    REM Check for requirements.txt and install if it exists
    if exist "%BASE_DIR%\requirements.txt" (
        echo Installing requirements from requirements.txt...
        "%PYTHON_EXE%" -m pip install -r "%BASE_DIR%\requirements.txt" --no-warn-script-location
    ) else (
        echo Warning: requirements.txt not found. Skipping package installation.
    )
    "%PYTHON_EXE%" "%MAIN_PY%"
    goto :eof
)

echo Python installation not found. Setting up environment...

REM =====================================================================
REM Define variables for setup process
REM =====================================================================
set "PYTHON_ZIP=%TEMP%\python-3.12.10-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip"
set "REQUIREMENTS_FILE=%BASE_DIR%\requirements.txt"

REM =====================================================================
REM Create Python directory
REM =====================================================================
echo Creating Python directory...
mkdir "%PYTHON_DIR%"

REM =====================================================================
REM Download and extract Python embedded distribution
REM Uses PowerShell to download the file and extract it
REM =====================================================================
echo Downloading Python embedded distribution...
powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'"

echo Extracting Python...
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"

REM =====================================================================
REM Set up pip in the embedded Python distribution
REM 1. Check if requirements.txt exists, create if not
REM 2. Enable site-packages by modifying the _pth file
REM 3. Download and run get-pip.py to install pip
REM 4. Install required packages from requirements.txt
REM =====================================================================
echo Setting up pip...

REM Create requirements.txt if it doesn't exist
if not exist "%REQUIREMENTS_FILE%" (
    echo Creating empty requirements.txt file...
    echo. > "%REQUIREMENTS_FILE%"
)

REM Enable site-packages in embedded Python by modifying python*._pth file
REM This is required for pip to work in embedded distribution
for %%F in ("%PYTHON_DIR%\python*._pth") do (
    type "%%F" > "%%F.tmp"
    echo import site >> "%%F.tmp"
    move /y "%%F.tmp" "%%F"
)

REM Download get-pip.py and install pip
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_DIR%\get-pip.py'"
"%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location

REM Upgrade pip to the latest version
echo Upgrading pip to the latest version...
"%PYTHON_DIR%\python.exe" -m pip install --upgrade pip --no-warn-script-location

REM Check if requirements.txt exists and install required packages
if exist "%REQUIREMENTS_FILE%" (
    echo Installing required packages from requirements.txt...
    "%PYTHON_DIR%\python.exe" -m pip install -r "%REQUIREMENTS_FILE%" --no-warn-script-location
) else (
    echo Warning: requirements.txt not found. Skipping package installation.
)

REM =====================================================================
REM Launch the application
REM =====================================================================
echo Setup complete. Running main.py...
"%PYTHON_EXE%" "%MAIN_PY%"

endlocal