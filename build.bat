@echo off
echo Building IVAO Weather Tool...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
python -m PyInstaller --onefile --windowed --name "IVAO Weather Tool" src/main.py

echo.
echo Build complete! Executable is in dist/
echo.
pause
