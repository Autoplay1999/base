@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/zlib"
call utils PrepareDest "../bin/zlib"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuildAll "zlib/zlib.vcxproj" || exit /b 1

call utils CopyRecursive "zlib/bin/lib" "../bin/zlib/lib"
call utils CopyHeaders "../modules/zlib" "../bin/zlib/include/zlib" "zconf.h"
call utils CopyHeaders "../modules/zlib" "../bin/zlib/include/zlib" "zlib.h"

if exist "zlib/bin" rd /S /Q "zlib/bin"

:: Apply Patch
sed -i "/#define ZCONF_H/a \
#define Z_PREFIX" "../bin/zlib/include/zlib/zconf.h" >nul 2>&1
