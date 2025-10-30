@echo off
setlocal EnableDelayedExpansion

set "_project=zydis"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"
set "_output=!_base!\msvc\bin"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init --recursive !_base! >nul 2>&1

call base
call "!vs_msbuildcmd!" >nul 2>&1
msbuild !_base!/msvc/!_project!.sln -p:Configuration="Release MT" -p:Platform=x64 -t:Zycore:Clean;Zycore:Rebuild;Zydis:Clean;Zydis:Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_base!/msvc/!_project!.sln -p:Configuration="Debug MT" -p:Platform=x64 -t:Zycore:Clean;Zycore:Rebuild;Zydis:Clean;Zydis:Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_base!/msvc/!_project!.sln -p:Configuration="Release MT" -p:Platform=x86 -t:Zycore:Clean;Zycore:Rebuild;Zydis:Clean;Zydis:Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_base!/msvc/!_project!.sln -p:Configuration="Debug MT" -p:Platform=x86 -t:Zycore:Clean;Zycore:Rebuild;Zydis:Clean;Zydis:Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
md "!_dest!\lib\x86\debug" "!_dest!\lib\x64\debug" "!_dest!\lib\x86\release" "!_dest!\lib\x64\release" "!_dest!\include" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\DebugX86" "!_dest!\lib\x86\debug" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\DebugX64" "!_dest!\lib\x64\debug" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\ReleaseX86" "!_dest!\lib\x86\release" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\ReleaseX64" "!_dest!\lib\x64\release" >nul 2>&1
xcopy /S /H /Y /R /I "!_base!\include" "!_dest!\include\" >nul 2>&1