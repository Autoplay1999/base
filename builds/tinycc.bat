@echo off
setlocal EnableDelayedExpansion

set "_project=tinycc"
set "_output=!_project!\bin"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"
set "_curdir=%~dp0"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init !_base! >nul 2>&1

call base
pushd "!_base!\win32"
call "!vs_vcvar32!" >nul 2>&1
call build-tcc -c cl >nul 2>&1
@echo off
if %ERRORLEVEL% neq 0 goto :eof
msbuild !_curdir!/!_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=Win32 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_curdir!/!_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=Win32 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
call "!vs_vcvar64!" >nul 2>&1
call build-tcc -c cl -t 32 >nul 2>&1
@echo off
msbuild !_curdir!/!_project!/!_project!.vcxproj -p:Configuration=Release -p:Platform=x64 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
msbuild !_curdir!/!_project!/!_project!.vcxproj -p:Configuration=Debug -p:Platform=x64 -t:Clean;Rebuild -v:q >nul 2>&1
if %ERRORLEVEL% neq 0 goto :EOF
popd
md "!_dest!\lib" "!_dest!\include" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\lib" "!_dest!\lib\" >nul 2>&1
xcopy /H /Y /R "!_base!\libtcc.h" "!_dest!\include\" >nul 2>&1
rd /S /Q "!_output!" >nul 2>&1