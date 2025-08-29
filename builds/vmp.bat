@echo off
setlocal EnableDelayedExpansion

set "_project=vmp"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

md "!_dest!\include" 2>nul
xcopy /H /Y /R "!_base!\include\*.h" "!_dest!\include\" 1>nul
xcopy /S /H /Y /R /I "!_base!\lib" "!_dest!\lib\" 1>nul
xcopy /S /H /Y /R /I "!_base!\bin" "!_dest!\bin\" 1>nul