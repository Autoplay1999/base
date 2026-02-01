@echo off
setlocal EnableDelayedExpansion

:: --- Dispatcher ---
if "%~1"==":InternalBuild" (
    set "_arch=%~2"
    set "_config=%~3"
    goto :InternalBuild
)

call "%~dp0base"

:: --- Configuration ---
set "_name=luajit"
set "_base=%~dp0..\modules\luajit"
set "_src=%_base%\src"
set "_bin=%~dp0..\bin\%_name%"

:: --- Setup ---
echo [INFO] Updating submodule...
call "%~dp0utils" UpdateSubmodule "../modules/luajit"

echo [INFO] Applying patch...
:: Reset to clean state before applying
git -C "%_base%" checkout src/msvcbuild.bat >nul 2>&1
git -C "%_base%" apply "%~dp0luajit.patch" || (
    echo [WARNING] Failed to apply patch. It might be already applied or incompatible.
)

if not exist "%_bin%" md "%_bin%" >nul 2>&1
if not exist "%_bin%\include" md "%_bin%\include" >nul 2>&1

:: --- Process Builds ---
:: Use cmd /c to isolate architectures and configurations
call :InvokeBuild x64 Release || exit /b 1
call :InvokeBuild x64 Debug || exit /b 1
call :InvokeBuild x86 Release || exit /b 1
call :InvokeBuild x86 Debug || exit /b 1

:: --- Headers ---
echo [INFO] Copying headers...
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "lua.h"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "luajit.h"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "lualib.h"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "lauxlib.h"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "lua.hpp"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "luaconf.h"
call "%~dp0utils" CopyHeaders "%_src%" "%_bin%\include" "luajit_relver.txt"

:: Copy JIT Library (Essential for full LuaJIT functionality)
echo [INFO] Copying JIT library...
if exist "%_bin%\include\jit" rd /S /Q "%_bin%\include\jit" >nul 2>&1
md "%_bin%\include\jit" >nul 2>&1
xcopy /S /Y /Q "%_src%\jit\*.lua" "%_bin%\include\jit\" >nul 2>&1

echo [SUCCESS] %_name% build completed successfully.
exit /b 0

:: -----------------------------------------------------------------------------
:: InvokeBuild [Arch] [Config] (Starts a new process for isolation)
:: -----------------------------------------------------------------------------
:InvokeBuild
echo [INFO] Building %_name% [%1/%2]...
cmd /c ""%~f0" :InternalBuild %1 %2"
exit /b %errorlevel%

:: -----------------------------------------------------------------------------
:: InternalBuild [Arch] [Config] (Runs inside the isolated process)
:: -----------------------------------------------------------------------------
:InternalBuild
:: Re-call base to set vs_vcvar* variables in the new process
call "%~dp0base"
set "_output=%_bin%\lib\%_arch%\%_config%"

:: Setup VS environment
if "%_arch%"=="x64" (
    call "!vs_vcvar64!" >nul 2>&1
) else (
    call "!vs_vcvar32!" >nul 2>&1
)

pushd "%_src%"

:: Clean up before build
if exist *.obj del /Q /F *.obj >nul 2>&1
if exist host\*.obj del /Q /F host\*.obj >nul 2>&1
if exist *.lib del /Q /F *.lib >nul 2>&1
if exist *.dll del /Q /F *.dll >nul 2>&1
if exist *.exe del /Q /F *.exe >nul 2>&1
if exist *.exp del /Q /F *.exp >nul 2>&1
if exist *.pdb del /Q /F *.pdb >nul 2>&1
if exist *.manifest del /Q /F *.manifest >nul 2>&1

:: Standard Flags
set "LJFLAGS=/GR- /EHsc"
if "%_config%"=="Release" (
    set "LJFLAGS=!LJFLAGS! /MT /O2"
    set "MSVC_ARGS=static"
) else (
    set "LJFLAGS=!LJFLAGS! /MTd /Zi /Od"
    set "MSVC_ARGS=debug static"
)

:: Inject flags via environment variable
set "LJCOMPILE=cl /nologo /c /W3 /D_CRT_SECURE_NO_DEPRECATE /D_CRT_STDIO_INLINE=__declspec(dllexport)__inline !LJFLAGS!"

echo   - Running msvcbuild...
call msvcbuild.bat !MSVC_ARGS!
if errorlevel 1 (
    echo [ERROR] msvcbuild.bat failed for %_arch%/%_config%
    popd
    exit /b 1
)

:: Move static lib
if not exist "%_output%" md "%_output%" >nul 2>&1
move /Y lua51.lib "%_output%\lua51.lib" >nul 2>&1
if exist lua51.pdb move /Y lua51.pdb "%_output%\lua51.pdb" >nul 2>&1

:: Clean up leftovers
if exist *.obj del /Q /F *.obj >nul 2>&1
if exist host\*.obj del /Q /F host\*.obj >nul 2>&1

popd
exit /b 0
