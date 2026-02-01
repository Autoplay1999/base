@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\KNSoft.NDK"
call "%~dp0utils" PrepareDest "%~dp0..\bin\KNSoft"

set "_base=%~dp0..\modules\KNSoft.NDK"
set "_sln=!_base!\Source\KNSoft.NDK.sln"
set "_bin=%~dp0..\bin\KNSoft"

call "%~dp0utils" NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
echo [INFO] Building KNSoft.NDK...
call "%~dp0utils" MSBuild "!_sln!" "Release" "x64" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Debug" "x64" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Release" "x86" || exit /b 1
call "%~dp0utils" MSBuild "!_sln!" "Debug" "x86" || exit /b 1

set "_out=!_base!\Source\OutDir"
echo [INFO] Organizing libraries...
for %%a in (x64 x86) do (
    for %%c in (release debug) do (
        set "_dst=!_bin!\lib\%%a\%%c"
        if not exist "!_dst!" md "!_dst!" >nul 2>&1
        
        :: NDK libs are in the arch root
        if exist "!_out!\%%a\KNSoft.NDK.Ntdll.CRT.lib" copy /y "!_out!\%%a\KNSoft.NDK.Ntdll.CRT.lib" "!_dst!\" >nul
        if exist "!_out!\%%a\KNSoft.NDK.Ntdll.Hash.lib" copy /y "!_out!\%%a\KNSoft.NDK.Ntdll.Hash.lib" "!_dst!\" >nul
        if exist "!_out!\%%a\KNSoft.NDK.WinAPI.lib" copy /y "!_out!\%%a\KNSoft.NDK.WinAPI.lib" "!_dst!\" >nul
        echo [DONE] Collected %%a/%%c libs.
    )
)

echo [INFO] Copying headers...
call "%~dp0utils" PrepareDest "!_bin!\include"
:: Use CopyHeaders with pattern but WITHOUT subdirectories for the root if needed, 
:: or just copy the whole Include folder with pattern. 
:: NDK headers are nested, so CopyHeaders is actually what we want, but we must be careful.
:: The previous messy directories were from SlimDetours/Syscall, not NDK.
call "%~dp0utils" CopyHeaders "!_base!\Source\Include" "!_bin!\include" "*.h"
call "%~dp0utils" CopyHeaders "!_base!\Source\Include" "!_bin!\include" "*.inl"

echo [SUCCESS] KNSoft.NDK build completed successfully.
