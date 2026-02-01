@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\asmjit"
call "%~dp0utils" PrepareDest "%~dp0..\bin\asmjit"

:: Activate VS Environment (for CMake, etc.)
call "!vs_devcmd!" -no_logo >nul 2>&1

set "_base=%~dp0..\modules\asmjit"
set "_build=%_base%\build"
set "_bin=%~dp0..\bin\asmjit"

:: Enforce: Static Runtime, No GL, No RTTI
set "_common_args=-DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF -DCMAKE_CXX_FLAGS="/GR- /EHsc" -DCMAKE_C_FLAGS="/GR-""

:: Build configurations
for %%a in (x64 Win32) do (
    for %%c in (Release Debug) do (
        set "_arch=%%a"
        set "_plat=%%a"
        if "%%a"=="Win32" set "_plat=x86"
        
        set "_conf=%%c"
        set "_conf_lower=%%c"
        if "%%c"=="Release" set "_conf_lower=release"
        if "%%c"=="Debug" set "_conf_lower=debug"
        
        :: Set Runtime Library
        set "_runtime=MultiThreaded"
        if "%%c"=="Debug" set "_runtime=MultiThreadedDebug"
        
        echo [INFO] Building asmjit [!_plat!/%%c]...
        set "_curr_build=%_build%\!_plat!\!_conf_lower!"
        
        cmake "%_base%" -B "!_curr_build!" -G"Visual Studio 17 2022" -A "%%a" %_common_args% -DCMAKE_MSVC_RUNTIME_LIBRARY=!_runtime! || exit /b 1
        cmake --build "!_curr_build!" --config "%%c" --target asmjit -- -m || exit /b 1
        
        set "_dst_lib=%_bin%\lib\!_plat!\!_conf_lower!"
        
        call "%~dp0utils" PrepareDest "!_dst_lib!"
        if exist "!_curr_build!\%%c\asmjit.lib" (
            copy /y "!_curr_build!\%%c\asmjit.lib" "!_dst_lib!\" >nul
        )
    )
)

echo [INFO] Copying headers...
call "%~dp0utils" PrepareDest "%_bin%\include\asmjit"
call "%~dp0utils" CopyHeaders "%_base%\asmjit" "%_bin%\include\asmjit" "*.h"

echo [SUCCESS] asmjit build completed successfully.