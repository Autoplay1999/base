@echo off
setlocal EnableDelayedExpansion

set "_project=json"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" >nul 2>&1
xcopy /S /H /Y /R /I "!_base!\single_include" "!_dest!\include\" >nul 2>&1
xcopy /H /Y /R "!_base!\nlohmann_json.natvis" "!_dest!\" >nul 2>&1