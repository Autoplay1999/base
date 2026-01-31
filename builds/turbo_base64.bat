@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\Turbo-Base64"
call utils PrepareDest "..\bin\turbo_base64"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuildAll "turbo-base64\turbo-base64.vcxproj" || exit /b 1

call utils CopyRecursive "turbo-base64\bin\lib" "..\bin\turbo_base64\lib"
call utils CopyHeaders "..\modules\Turbo-Base64" "..\bin\turbo_base64\include" "turbob64.h"

if exist "turbo-base64\bin" rd /S /Q "turbo-base64\bin"
