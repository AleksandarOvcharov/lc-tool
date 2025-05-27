@echo off
echo Building LineCounter executable...
echo.

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist LineCounter.spec del LineCounter.spec

REM Build the executable
pyinstaller --onefile --windowed --name="LineCounter" --icon=NONE line_counter_gui.py

REM Check if build was successful
if exist dist\LineCounter.exe (
    echo.
    echo ===================================
    echo Build completed successfully!
    echo Executable location: dist\LineCounter.exe
    echo File size: 
    for %%I in (dist\LineCounter.exe) do echo %%~zI bytes
    echo ===================================
    echo.
    echo You can now distribute the LineCounter.exe file
    echo It runs standalone without requiring Python installation.
) else (
    echo.
    echo ===================================
    echo Build failed! Check the output above for errors.
    echo ===================================
)

pause 