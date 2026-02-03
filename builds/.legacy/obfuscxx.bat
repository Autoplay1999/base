@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\obfuscxx"
call "%~dp0utils" PrepareDest "%~dp0..\bin\obfuscxx"

echo [INFO] Organizing headers...
call "%~dp0utils" PrepareDest "%~dp0..\bin\obfuscxx\include"
copy /y "%~dp0..\modules\obfuscxx\obfuscxx\include\obfuscxx.h" "%~dp0..\bin\obfuscxx\include\" >nul

echo [SUCCESS] obfuscxx build completed successfully.