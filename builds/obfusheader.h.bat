@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\obfusheader.h"
call "%~dp0utils" PrepareDest "%~dp0..\bin\obfusheader.h"

echo [INFO] Organizing headers...
call "%~dp0utils" PrepareDest "%~dp0..\bin\obfusheader.h\include"
copy /y "%~dp0..\modules\obfusheader.h\include\obfusheader.h" "%~dp0..\bin\obfusheader.h\include\" >nul

echo [SUCCESS] obfusheader.h build completed successfully.