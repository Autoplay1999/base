@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\yaml-cpp"
call "%~dp0utils" PrepareDest "%~dp0..\bin\yaml-cpp"

:: Activate VS Environment
call "!vs_devcmd!" -no_logo >nul 2>&1

echo [INFO] Building yaml-cpp...
call "%~dp0utils" MSBuildAll "yaml-cpp\yaml-cpp.vcxproj" || exit /b 1

echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_plat=%%a"
        if "%%a"=="x86" set "_plat=Win32"
        
        set "_conf=%%c"
        if "%%c"=="release" set "_conf=Release"
        if "%%c"=="debug" set "_conf=Debug"
        
        set "_src=yaml-cpp\bin\lib\!_plat!\!_conf!"
        set "_dst=%~dp0..\bin\yaml-cpp\lib\%%a\%%c"
        
        md "!_dst!" >nul 2>&1
        if exist "!_src!\yaml-cpp.lib" (
            copy /y "!_src!\yaml-cpp.lib" "!_dst!\" >nul 2>&1
        )
    )
)

echo [INFO] Copying headers...
call "%~dp0utils" CopyHeaders "%~dp0..\modules\yaml-cpp\include" "%~dp0..\bin\yaml-cpp\include" "*.h"

echo [INFO] Patching dll.h...
set "_inc=%~dp0..\bin\yaml-cpp\include\yaml-cpp"
set "_target=%_inc%\dll.h"
if exist "!_target!" (
    sed -i "/#define DLL_H_/a \#define YAML_CPP_STATIC_DEFINE" "!_target!"
)

if exist "yaml-cpp\bin" rd /S /Q "yaml-cpp\bin"

echo [SUCCESS] yaml-cpp build completed successfully.
