@echo off
echo Starting Gasmet Gas Flux Analyzer...
python gasmet_analyzer.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo.
    echo Possible solutions:
    echo 1. Make sure Python is installed
    echo 2. Install required packages: pip install pandas numpy matplotlib scipy openpyxl
    echo.
    pause
)
