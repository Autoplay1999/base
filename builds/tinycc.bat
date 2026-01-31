@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\tinycc"
call utils PrepareDest "..\bin\tinycc"

:: Activate VS Environment (Global check)
call "!vs_devcmd!" -no_logo >nul 2>&1

set "_curdir=%~dp0"
if "%_curdir:~-1%"=="\" set "_curdir=%_curdir:~0,-1%"

set "_utils=%_curdir%\utils.bat"
set "_vcxproj=%_curdir%\tinycc\tinycc.vcxproj"
set "_helper=%_curdir%\tinycc_helper.bat"

:: Build x86 (Isolated)
cmd /c ""!_helper!" x86 "!_utils!" "!_vcxproj!" "!vs_vcvar32!""
if errorlevel 1 exit /b 1

:: Build x64 (Isolated)
cmd /c ""!_helper!" x64 "!_utils!" "!_vcxproj!" "!vs_vcvar64!""
if errorlevel 1 exit /b 1

call utils CopyRecursive "tinycc\bin\lib" "..\bin\tinycc\lib"
call utils CopyHeaders "..\modules\tinycc" "..\bin\tinycc\include" "libtcc.h"

if exist "tinycc\bin" rd /S /Q "tinycc\bin"
