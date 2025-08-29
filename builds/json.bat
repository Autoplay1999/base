@echo off
setlocal EnableDelayedExpansion

set "_project=json"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" 2>nul
xcopy /S /H /Y /R /I "!_base!\single_include" "!_dest!\include\" 1>nul
xcopy /H /Y /R "!_base!\nlohmann_json.natvis" "!_dest!\" 1>nul