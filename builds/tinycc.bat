@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/tinycc"
call utils PrepareDest "../bin/tinycc"

set "_curdir=%~dp0"

pushd "../modules/tinycc/win32"
    call "!vs_vcvar32!" >nul 2>&1
    call build-tcc -c cl >nul 2>&1 || (popd & exit /b 1)
    
    call utils MSBuild "%_curdir%tinycc/tinycc.vcxproj" "Release" "Win32" || (popd & exit /b 1)
    call utils MSBuild "%_curdir%tinycc/tinycc.vcxproj" "Debug" "Win32" || (popd & exit /b 1)
    
    call "!vs_vcvar64!" >nul 2>&1
    call build-tcc -c cl -t 32 >nul 2>&1 || (popd & exit /b 1)
    
    call utils MSBuild "%_curdir%tinycc/tinycc.vcxproj" "Release" "x64" || (popd & exit /b 1)
    call utils MSBuild "%_curdir%tinycc/tinycc.vcxproj" "Debug" "x64" || (popd & exit /b 1)
popd

call utils CopyRecursive "tinycc/bin/lib" "../bin/tinycc/lib"
call utils CopyHeaders "../modules/tinycc" "../bin/tinycc/include" "libtcc.h"

if exist "tinycc/bin" rd /S /Q "tinycc/bin"
