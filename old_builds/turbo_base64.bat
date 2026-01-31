@echo off
setlocal EnableDelayedExpansion

set "_project=turbo-base64"
set "_output=!_project!\bin"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init --recursive ..\modules\Turbo-Base64 >nul 2>&1

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
md "!_dest!\lib" "!_dest!\include" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\lib" "!_dest!\lib\" >nul 2>&1
xcopy /H /Y /R "!_base!\turbob64.h" "!_dest!\include\" >nul 2>&1
rd /S /Q "!_output!" >nul 2>&1