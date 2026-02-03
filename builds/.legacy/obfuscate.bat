@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\Obfuscate"
call "%~dp0utils" PrepareDest "%~dp0..\bin\Obfuscate"

echo [INFO] Organizing headers...
call "%~dp0utils" PrepareDest "%~dp0..\bin\Obfuscate\include"
copy /y "%~dp0..\modules\Obfuscate\obfuscate.h" "%~dp0..\bin\Obfuscate\include\" >nul

echo [SUCCESS] Obfuscate build completed successfully.