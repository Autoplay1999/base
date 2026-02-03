@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\simdjson"
call utils PrepareDest "..\bin\simdjson"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuildAll "simdjson\simdjson.vcxproj" || exit /b 1

call utils CopyRecursive "simdjson\bin\lib" "..\bin\simdjson\lib"
call utils CopyHeaders "..\modules\simdjson\singleheader" "..\bin\simdjson\include\simdjson" "*.h"

if exist "simdjson\bin" rd /S /Q "simdjson\bin"