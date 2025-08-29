@echo off
setlocal EnableDelayedExpansion

set "_project=tinycc"
set "_output=!_project!\bin"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

call base
call "!vs_msbuildcmd!" 1>nul
msbuild !_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=x64 -t:Clean;Rebuild -v:m
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=x64 -t:Clean;Rebuild -v:m
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=Win32 -t:Clean;Rebuild -v:m
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=Win32 -t:Clean;Rebuild -v:m
if %ERRORLEVEL% neq 0 goto :EOF
md "!_dest!\lib" "!_dest!\include" 2>nul
xcopy /S /H /Y /R /I "!_output!\lib" "!_dest!\lib\" 1>nul
xcopy /H /Y /R "!_base!\libtcc.h" "!_dest!\include\" 1>nul
rd /S /Q "!_output!" 2>nul