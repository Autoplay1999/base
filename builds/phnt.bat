@echo off
setlocal EnableDelayedExpansion

set "_project=phnt"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" 2>nul
xcopy /S /H /Y /R /I "!_base!\*.h" "!_dest!\include\" 1>nul