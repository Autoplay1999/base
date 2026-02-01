@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\KNSoft.Syscall"
set "_base=%~dp0..\modules\KNSoft.Syscall"
set "_sln=!_base!\Source\KNSoft.Syscall.sln"
set "_bin=%~dp0..\bin\KNSoft"

call "%~dp0utils" NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
echo [INFO] Building KNSoft.Syscall...
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
        if exist "!_src!\KNSoft.Syscall.lib" copy /y "!_src!\KNSoft.Syscall.lib" "!_dst!\" >nul
        echo [DONE] Collected %%a/%%c syscall lib.
    )
)

echo [INFO] Copying headers...
set "_inc=!_bin!\include\KNSoft\Syscall"
if not exist "!_inc!" md "!_inc!" >nul 2>&1
:: Use direct copy to avoid pulling in IntDir/Thunks
set "_src_h=!_base!\Source\KNSoft.Syscall"
copy /y "!_src_h!\Syscall.h" "!_inc!\" >nul 2>&1
copy /y "!_src_h!\Syscall.Thunks.h" "!_inc!\" >nul 2>&1

echo [SUCCESS] KNSoft.Syscall build completed successfully.
