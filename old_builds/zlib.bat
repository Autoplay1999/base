@echo off
setlocal EnableDelayedExpansion

set "_project=zlib"
set "_output=!_project!\bin"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init --recursive !_base! >nul 2>&1

call base
call "!vs_msbuildcmd!" >nul 2>&1
msbuild !_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=x64 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=x64 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=Win32 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=Win32 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
md "!_dest!\lib" "!_dest!\include\!_project!" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\lib" "!_dest!\lib\" >nul 2>&1
xcopy /H /Y /R "!_base!\zconf.h" "!_dest!\include\!_project!\" >nul 2>&1
xcopy /H /Y /R "!_base!\zlib.h" "!_dest!\include\!_project!\" >nul 2>&1
rd /S /Q "!_output!" >nul 2>&1
sed -i "/#define ZCONF_H/a \\\n#define Z_PREFIX" "!_dest!\include\!_project!\zconf.h" >nul 2>&1