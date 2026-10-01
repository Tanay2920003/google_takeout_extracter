@echo off
echo Starting Google Takeout Extractor...
python "%~dp0app.py"
if errorlevel 1 (
    echo.
    echo ERROR: Could not start the app.
    echo Make sure Python 3 is installed and available in PATH.
    pause
)
