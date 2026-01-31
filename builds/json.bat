@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/json"
call utils PrepareDest "../bin/json/include"
call utils CopyRecursive "../modules/json/single_include" "../bin/json/include"
xcopy /H /Y /R "../modules/json/nlohmann_json.natvis" "../bin/json/" >nul 2>&1