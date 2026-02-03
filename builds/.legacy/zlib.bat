@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\zlib"
call "%~dp0utils" PrepareDest "%~dp0..\bin\zlib"

:: Activate VS Environment
call "!vs_devcmd!" -no_logo >nul 2>&1

:: Build using MSBuild
echo [INFO] Building zlib...
call "%~dp0utils" MSBuildAll "zlib\zlib.vcxproj" || exit /b 1

:: Copy Libraries (Only .lib files)
echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_config=%%c"
        if "%%c"=="release" set "_config=Release"
        if "%%c"=="debug" set "_config=Debug"
        
        :: In this project, both x64 and x86 use their own names in the bin/lib folder
        set "_src=zlib\bin\lib\%%a\!_config!"
        set "_dst=%~dp0..\bin\zlib\lib\%%a\%%c"
        
        md "!_dst!" >nul 2>&1
        if exist "!_src!\zlib.lib" (
            copy /y "!_src!\zlib.lib" "!_dst!\" >nul 2>&1
        )
    )
)

:: Copy Headers (Only necessary ones)
echo [INFO] Copying headers...
set "_inc=%~dp0..\bin\zlib\include\zlib"
md "%_inc%" >nul 2>&1
copy /y "%~dp0..\modules\zlib\zlib.h" "%_inc%\" >nul 2>&1
copy /y "%~dp0..\modules\zlib\zconf.h" "%_inc%\" >nul 2>&1

:: Apply Patch to zconf.h
echo [INFO] Patching zconf.h...
set "_target=%_inc%\zconf.h"
if exist "!_target!" (
    sed -i "/#define ZCONF_H/a \\#define Z_PREFIX" "!_target!"
)

if exist "zlib\bin" rd /S /Q "zlib\bin"

echo [SUCCESS] zlib build completed successfully.
