@echo off
setlocal EnableDelayedExpansion
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\zydis"

:: --- Build Versioning ---
set "_version=1"
call "%~dp0utils" CheckBuildVersion "%~dp0..\bin\zydis" "%_version%"
if "!_build_needed!"=="0" exit /b 0

call "%~dp0utils" PrepareDest "%~dp0..\bin\zydis"

:: Activate VS Environment
call "!vs_devcmd!" -no_logo >nul 2>&1

set "_base=%~dp0..\modules\zydis"
set "_bin=%~dp0..\bin\zydis"

:: Standard Flags + Exclude targets
set "_common_args=-DZYDIS_BUILD_EXAMPLES=OFF -DZYDIS_BUILD_TOOLS=OFF -DZYDIS_BUILD_TESTS=OFF -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF -DCMAKE_CXX_FLAGS="/GR- /EHsc" -DCMAKE_C_FLAGS="/GR-""

:: x86 Release
echo [INFO] Building zydis [x86/Release]...
set "_build=%_base%\build\x86\release"
cmake "%_base%" -B "%_build%" -G"Visual Studio 17 2022" -A "Win32" !_common_args! -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded || exit /b 1
cmake --build "%_build%" --config "Release" --target Zydis -- -m || exit /b 1
call "%~dp0utils" PrepareDest "%_bin%\lib\x86\release"
call "%~dp0utils" CopyRecursive "%_build%\Release" "%_bin%\lib\x86\release"
copy /y "%_build%\zycore\Release\Zycore.lib" "%_bin%\lib\x86\release\" >nul

:: x86 Debug
echo [INFO] Building zydis [x86/Debug]...
set "_build=%_base%\build\x86\debug"
cmake "%_base%" -B "%_build%" -G"Visual Studio 17 2022" -A "Win32" !_common_args! -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDebug || exit /b 1
cmake --build "%_build%" --config "Debug" --target Zydis -- -m || exit /b 1
call "%~dp0utils" PrepareDest "%_bin%\lib\x86\debug"
call "%~dp0utils" CopyRecursive "%_build%\Debug" "%_bin%\lib\x86\debug"
copy /y "%_build%\zycore\Debug\Zycore.lib" "%_bin%\lib\x86\debug\" >nul

:: x64 Release
echo [INFO] Building zydis [x64/Release]...
set "_build=%_base%\build\x64\release"
cmake "%_base%" -B "%_build%" -G"Visual Studio 17 2022" -A "x64" !_common_args! -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded || exit /b 1
cmake --build "%_build%" --config "Release" --target Zydis -- -m || exit /b 1
call "%~dp0utils" PrepareDest "%_bin%\lib\x64\release"
call "%~dp0utils" CopyRecursive "%_build%\Release" "%_bin%\lib\x64\release"
copy /y "%_build%\zycore\Release\Zycore.lib" "%_bin%\lib\x64\release\" >nul

:: x64 Debug
echo [INFO] Building zydis [x64/Debug]...
set "_build=%_base%\build\x64\debug"
cmake "%_base%" -B "%_build%" -G"Visual Studio 17 2022" -A "x64" !_common_args! -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDebug || exit /b 1
cmake --build "%_build%" --config "Debug" --target Zydis -- -m || exit /b 1
call "%~dp0utils" PrepareDest "%_bin%\lib\x64\debug"
call "%~dp0utils" CopyRecursive "%_build%\Debug" "%_bin%\lib\x64\debug"
copy /y "%_build%\zycore\Debug\Zycore.lib" "%_bin%\lib\x64\debug\" >nul

echo [INFO] Copying headers...
call "%~dp0utils" PrepareDest "%_bin%\include"
call "%~dp0utils" CopyHeaders "%_base%\include" "%_bin%\include" "*.h"
call "%~dp0utils" CopyHeaders "%_base%\dependencies\zycore\include" "%_bin%\include" "*.h"

:: Update build version
call "%~dp0utils" WriteBuildVersion "%_bin%" "%_version%"

echo [SUCCESS] zydis build completed successfully.
