@echo off
setlocal EnableDelayedExpansion

set "_project=yacppl"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init --recursive !_base! >nul 2>&1

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\include\*.hpp" "!_dest!\include\" >nul 2>&1