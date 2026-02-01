@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\KNSoft.SlimDetours"
set "_base=%~dp0..\modules\KNSoft.SlimDetours"
set "_sln=!_base!\Source\KNSoft.SlimDetours.sln"
set "_bin=%~dp0..\bin\KNSoft"

call "%~dp0utils" NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
echo [INFO] Building KNSoft.SlimDetours...
call "%~dp0utils" MSBuild "!_sln!" "Release" "x64" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Debug" "x64" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Release" "x86" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Debug" "x86" || exit /b 1

set "_out=!_base!\Source\OutDir"
echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_conf=%%c"
        if "%%c"=="release" set "_conf=Release"
        if "%%c"=="debug" set "_conf=Debug"
        
        set "_src=!_out!\%%a\!_conf!"
        set "_dst=!_bin!\lib\%%a\%%c"
        
        if not exist "!_dst!" md "!_dst!" >nul 2>&1
        if exist "!_src!\KNSoft.SlimDetours.lib" copy /y "!_src!\KNSoft.SlimDetours.lib" "!_dst!\" >nul
        if exist "!_src!\Microsoft.Detours.lib" copy /y "!_src!\Microsoft.Detours.lib" "!_dst!\" >nul
        echo [DONE] Collected %%a/%%c slimdetours libs.
    )
)

echo [INFO] Copying headers...
set "_inc=!_bin!\include\KNSoft\SlimDetours"
if not exist "!_inc!" md "!_inc!" >nul 2>&1
:: Use direct copy to avoid pulling in IntDir/Thunks
set "_src_h=!_base!\Source\KNSoft.SlimDetours"
copy /y "!_src_h!\SlimDetours.h" "!_inc!\" >nul 2>&1
copy /y "!_src_h!\SlimDetours.inl" "!_inc!\" >nul 2>&1
copy /y "!_src_h!\SlimDetours.NDK.inl" "!_inc!\" >nul 2>&1

echo [SUCCESS] KNSoft.SlimDetours build completed successfully.
