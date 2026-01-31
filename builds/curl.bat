@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/curl"
call utils PrepareDest "../bin/curl"

set "_base=../modules/curl"
set "_build=../bin/curl/_curl"

:: Fix Deprecation Warning (Global)
set "WINBUILD_ACKNOWLEDGE_DEPRECATED=yes"

pushd "!_base!"
    git checkout curl-8_16_0 >nul 2>&1
popd

call utils CopyRecursive "!_base!" "!_build!"

:: Build x64
cmd /c "call "!vs_vcvar64!" >nul 2>&1 && cd /d "!_build!\winbuild" && nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=yes GEN_PDB=yes MACHINE=x64 >nul 2>&1 && nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=no GEN_PDB=no MACHINE=x64 >nul 2>&1"
if errorlevel 1 exit /b 1

:: Build x86
cmd /c "call "!vs_vcvar32!" >nul 2>&1 && cd /d "!_build!\winbuild" && nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=yes GEN_PDB=yes MACHINE=x86 >nul 2>&1 && nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=no GEN_PDB=no MACHINE=x86 >nul 2>&1"
if errorlevel 1 exit /b 1

set "_out=!_build!/builds"
call utils CopyRecursive "!_out!/libcurl-vc-x64-debug-static-ipv6-sspi-schannel/lib" "../bin/curl/lib/x64"
call utils CopyRecursive "!_out!/libcurl-vc-x64-release-static-ipv6-sspi-schannel/lib" "../bin/curl/lib/x64"
call utils CopyRecursive "!_out!/libcurl-vc-x86-debug-static-ipv6-sspi-schannel/lib" "../bin/curl/lib/x86"
call utils CopyRecursive "!_out!/libcurl-vc-x86-release-static-ipv6-sspi-schannel/lib" "../bin/curl/lib/x86"

call utils CopyHeaders "!_build!/include/curl" "../bin/curl/include/curl" "*.h"

rd /S /Q "!_build!" >nul 2>&1