@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\Turbo-Base64"
call "%~dp0utils" PrepareDest "%~dp0..\bin\turbo_base64"

:: Activate VS Environment
call "!vs_msbuildcmd!" >nul 2>&1

echo [INFO] Building turbo-base64...
:: Build using MSBuild
call "%~dp0utils" MSBuildAll "turbo-base64\turbo-base64.vcxproj" || exit /b 1

echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_arch=%%a"
        set "_plat=%%a"
        if "%%a"=="x86" set "_plat=Win32"
        
        set "_conf=%%c"
        if "%%c"=="release" set "_conf=Release"
        if "%%c"=="debug" set "_conf=Debug"
        
        :: Source path matches $(SolutionDir)bin\lib\$(Platform)\$(Configuration)\ in vcxproj
        :: Wait, vcxproj uses x86 and x64 in OutDir paths explicitly
        set "_src=turbo-base64\bin\lib\!_arch!\!_conf!"
        set "_dst=%~dp0..\bin\turbo_base64\lib\!_arch!\%%c"
        
        if not exist "!_dst!" md "!_dst!" >nul 2>&1
        if exist "!_src!\turbo-base64.lib" (
            copy /y "!_src!\turbo-base64.lib" "!_dst!\" >nul 2>&1
            echo [DONE] Collected !_arch!/%%c lib.
        ) else (
            echo [WARNING] Missing !_arch!/%%c lib at !_src!
        )
    )
)

echo [INFO] Copying headers...
:: Only copy necessary headers from root, specifically turbob64.h
call "%~dp0utils" PrepareDest "%~dp0..\bin\turbo_base64\include"
copy /y "%~dp0..\modules\Turbo-Base64\turbob64.h" "%~dp0..\bin\turbo_base64\include\" >nul

if exist "turbo-base64\bin" rd /S /Q "turbo-base64\bin"

echo [SUCCESS] turbo-base64 build completed successfully.
