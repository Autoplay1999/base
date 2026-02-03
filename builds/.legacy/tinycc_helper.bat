@echo off
setlocal EnableDelayedExpansion
set "_arch=%~1"
set "_utils=%~2"
set "_vcxproj=%~3"
set "_vs_env=%~4"

call "!_vs_env!" >nul 2>&1
pushd ..\modules\tinycc\win32

if "%_arch%"=="x86" (
    call build-tcc -c cl >nul 2>&1
    set "_plat=Win32"
) else (
    call build-tcc -c cl -t 32 >nul 2>&1
    set "_plat=x64"
)

if errorlevel 1 (
    echo [ERROR] build-tcc failed for %_arch%
    exit /b 1
)

:: Debug echo
echo [DEBUG] Helper building %_arch% (%_plat%)...

call "%_utils%" MSBuild "%_vcxproj%" "Release" "%_plat%"
if errorlevel 1 exit /b 1
call "%_utils%" MSBuild "%_vcxproj%" "Debug" "%_plat%"
if errorlevel 1 exit /b 1

exit /b 0
