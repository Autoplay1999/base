@echo off
setlocal EnableDelayedExpansion

set "_project=xorstr"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" 2>nul
xcopy /S /H /Y /R /I "!_base!\include\*.hpp" "!_dest!\include\" 1>nul