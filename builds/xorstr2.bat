@echo off
setlocal EnableDelayedExpansion

set "_project=xorstr2"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init !_base! >nul 2>&1

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\include\*.h" "!_dest!\include\" >nul 2>&1
sed -i -e "/#define xorstr(s)/s/xorstr/xorstr2/" "!_dest!\include\xorstr.h"