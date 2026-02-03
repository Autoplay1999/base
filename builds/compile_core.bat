@echo off
setlocal
cd /d "%~dp0"

echo [INFO] Compiling Core Utilities...

:: Install Dependencies
call install_deps.bat
if %ERRORLEVEL% NEQ 0 exit /b 1

:: Compile
python setup_cython.py build_ext --inplace
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Compilation failed.
    pause
    exit /b 1
)

echo [SUCCESS] Core Utilities Compiled to Native Code.
pause
