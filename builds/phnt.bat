@echo off
setlocal EnableDelayedExpansion

set "_project=phnt"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\*.h" "!_dest!\include\" >nul 2>&1