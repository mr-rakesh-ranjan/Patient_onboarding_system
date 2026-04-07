@echo off
echo ========================================
echo  Patient Onboarding System
echo  Starting Streamlit Application...
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet

:: Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your service URLs
    echo See .env.example for reference
    echo.
    pause
)

:: Launch Streamlit
echo.
echo ========================================
echo  Launching application...
echo  The app will open in your browser
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run main.py

pause
