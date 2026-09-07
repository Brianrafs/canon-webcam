@echo off
echo ==========================================
echo   Canon T5i Webcam - Setup
echo ==========================================
echo.

echo [1/3] Checking Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Install from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo OK - Python found

echo.
echo [2/3] Installing dependencies...
pip install opencv-python pyvirtualcam numpy Pillow

echo.
echo [3/3] Done!
echo.
echo To run: python main.py
echo.
pause
