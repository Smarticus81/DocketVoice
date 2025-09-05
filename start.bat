@echo off
echo Voice-Driven Bankruptcy Filing Assistant
echo ======================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking dependencies...
python -c "import openai, pygame, elevenlabs" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing now...
    echo.
    call install_deps.bat
    if errorlevel 1 (
        echo Failed to install dependencies. Please run install_deps.bat manually.
        pause
        exit /b 1
    )
) else (
    echo All dependencies are installed.
)

echo.
echo Choose an option:
echo 1. Test Voice System (recommended first)
echo 2. Run Main Bankruptcy Application
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting voice system test...
    python test_voice.py
) else if "%choice%"=="2" (
    echo.
    echo Starting the main application...
    python agent.py
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Starting main application...
    python agent.py
)

echo.
echo Application finished. Press any key to exit.
pause 