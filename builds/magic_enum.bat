@echo off
setlocal EnableDelayedExpansion

set "_project=magic_enum"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\include\*.hpp" "!_dest!\include\" >nul 2>&1