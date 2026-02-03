@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\tinycc"

:: --- Build Versioning ---
set "_version=1"
call "%~dp0utils" CheckBuildVersion "%~dp0..\bin\tinycc" "%_version%"
if "!_build_needed!"=="0" exit /b 0

call "%~dp0utils" PrepareDest "%~dp0..\bin\tinycc"

:: Activate VS Environment (Global check)
call "!vs_devcmd!" -no_logo >nul 2>&1

set "_curdir=%~dp0"
if "%_curdir:~-1%"=="\" set "_curdir=%_curdir:~0,-1%"

set "_utils=%_curdir%\utils.bat"
set "_vcxproj=%_curdir%\tinycc\tinycc.vcxproj"
set "_helper=%_curdir%\tinycc_helper.bat"

:: Build x86 (Isolated)
echo [INFO] Building TinyCC [x86]...
cmd /c ""!_helper!" x86 "!_utils!" "!_vcxproj!" "!vs_vcvar32!""
if errorlevel 1 exit /b 1

:: Build x64 (Isolated)
echo [INFO] Building TinyCC [x64]...
cmd /c ""!_helper!" x64 "!_utils!" "!_vcxproj!" "!vs_vcvar64!""
if errorlevel 1 exit /b 1

echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_arch=%%a"
        set "_plat=%%a"
        if "%%a"=="x86" set "_plat=Win32"
        
        set "_conf=%%c"
        if "%%c"=="release" set "_conf=Release"
        if "%%c"=="debug" set "_conf=Debug"
        
        set "_src=tinycc\bin\lib\!_arch!\!_conf!"
        set "_dst=%~dp0..\bin\tinycc\lib\!_arch!\%%c"
        
        if not exist "!_dst!" md "!_dst!" >nul 2>&1
        if exist "!_src!\tinycc.lib" (
            copy /y "!_src!\tinycc.lib" "!_dst!\" >nul 2>&1
            echo [DONE] Collected !_arch!/%%c lib.
        )
    )
)

echo [INFO] Copying headers...
:: Only copy necessary libtcc.h
call "%~dp0utils" PrepareDest "%~dp0..\bin\tinycc\include"
copy /y "%~dp0..\modules\tinycc\libtcc.h" "%~dp0..\bin\tinycc\include\" >nul

if exist "tinycc\bin" rd /S /Q "tinycc\bin"

:: Update build version
call "%~dp0utils" WriteBuildVersion "%~dp0..\bin\tinycc" "%_version%"

echo [SUCCESS] tinycc build completed successfully.
