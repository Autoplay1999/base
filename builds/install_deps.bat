@echo off
setlocal
cd /d "%~dp0"

echo [INFO] Installing Python Dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --quiet

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies are up to date.
