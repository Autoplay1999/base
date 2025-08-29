@echo off
setlocal EnableDelayedExpansion

set "_project=nameof"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" 2>nul
xcopy /H /Y /R "!_base!\include\*.hpp" "!_dest!\include\" 1>nul