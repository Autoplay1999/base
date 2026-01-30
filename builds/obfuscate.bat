@echo off
setlocal EnableDelayedExpansion
call base

set "_project=Obfuscate"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if not exist !_base! git restore !_base!

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\obfuscate.h" "!_dest!\include\" >nul 2>&1

