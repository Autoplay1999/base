@echo off
setlocal EnableDelayedExpansion

set "_project=json"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init !_base! >nul 2>&1

md "!_dest!\include" >nul 2>&1
xcopy /S /H /Y /R /I "!_base!\single_include" "!_dest!\include\" >nul 2>&1
xcopy /H /Y /R "!_base!\nlohmann_json.natvis" "!_dest!\" >nul 2>&1