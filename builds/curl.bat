@echo off
setlocal EnableDelayedExpansion

:: Dispatcher for internal calls
if "%~1"==":InternalBuild" (
    call :InternalBuild %2
    exit /b !errorlevel!
)

call base
call utils UpdateSubmodule "../modules/curl"
call utils PrepareDest "../bin/curl"

set "_base=../modules/curl"
set "_build_root=../bin/curl/_build"

:: CMake Arguments
:: Removed CURL_ZLIB=OFF, Added CURL_ZLIB=ON and overrides in LocalCMakeBuild
set "CMAKE_GEN=-G "NMake Makefiles""
set "CMAKE_ARGS=-DBUILD_SHARED_LIBS=OFF -DCURL_USE_SCHANNEL=ON -DCURL_USE_OPENSSL=OFF -DENABLE_UNICODE=ON -DENABLE_IPV6=ON -DCURL_WINDOWS_SSPI=ON -DBUILD_CURL_EXE=OFF -DBUILD_TESTING=OFF -DCURL_STATIC_CRT=ON -DCURL_USE_LIBPSL=OFF -DCURL_use_LIBSSH2=OFF -DCURL_USE_LIBIDN2=OFF -DCURL_BROTLI=OFF -DCURL_ZSTD=OFF -DUSE_NGHTTP2=OFF"

:: Build x64
echo [INFO] Building x64...
cmd /c "call "!vs_vcvar64!" >nul 2>&1 && call "%~f0" :InternalBuild x64"
if errorlevel 1 (
    echo [ERROR] Build x64 failed.
    exit /b 1
)

:: Build x86
echo [INFO] Building x86...
cmd /c "call "!vs_vcvar32!" >nul 2>&1 && call "%~f0" :InternalBuild Win32"
if errorlevel 1 (
    echo [ERROR] Build x86 failed.
    exit /b 1
)

:: Copy Headers
echo [INFO] Copying headers...
call utils CopyHeaders "!_base!/include/curl" "../bin/curl/include/curl" "*.*"

:: Clean up
echo [INFO] Cleaning up...
rd /S /Q "!_build_root!" >nul 2>&1

echo [SUCCESS] Curl build complete.
exit /b 0

:: -----------------------------------------------------------------------------
:: Helper: Internal Build [Arch] (Runs inside vcvars env)
:: -----------------------------------------------------------------------------
:InternalBuild
set "_arch=%~1"
set "_build_dir=%_build_root%/%_arch%"

:: Debug Build
echo   - Debug [%_arch%]...
call :LocalCMakeBuild "%_base%" "%_build_dir%/Debug" "%_arch%" "Debug" "%CMAKE_ARGS% -DCMAKE_DEBUG_POSTFIX=-d"
if errorlevel 1 exit /b 1
call :CopyLibs "%_build_dir%/Debug" "%_arch%"

:: Release Build
echo   - Release [%_arch%]...
call :LocalCMakeBuild "%_base%" "%_build_dir%/Release" "%_arch%" "Release" "%CMAKE_ARGS%"
if errorlevel 1 exit /b 1
call :CopyLibs "%_build_dir%/Release" "%_arch%"
exit /b 0

:: -----------------------------------------------------------------------------
:: Helper: Local CMake Build (Verbose)
:: -----------------------------------------------------------------------------
:LocalCMakeBuild
set "_src=%~1"
set "_bld=%~2"
set "_arc=%~3"
set "_cfg=%~4"
set "_opt=%~5"

:: ZLIB Configuration
set "_z_arch=%_arc%"
if /i "%_z_arch%"=="Win32" set "_z_arch=x86"

:: Path to zlib.lib (e.g., ../bin/zlib/lib/x64/debug/zlib.lib)
set "_z_lib=../bin/zlib/lib/%_z_arch%/%_cfg%/zlib.lib"
set "_z_inc=../bin/zlib/include/zlib"

:: Verify Zlib existence
if not exist "%_z_lib%" (
    echo [ERROR] Zlib library not found at: %_z_lib%
    exit /b 1
)

set "ZLIB_FLAGS=-DCURL_ZLIB=ON -DZLIB_INCLUDE_DIR="%_z_inc%" -DZLIB_LIBRARY="%_z_lib%""

cmake -S "%_src%" -B "%_bld%" %CMAKE_GEN% -DCMAKE_BUILD_TYPE=%_cfg% %_opt% %ZLIB_FLAGS%
if errorlevel 1 (
    echo [ERROR] CMake Configure failed for %_cfg%/%_arc%
    exit /b 1
)

cmake --build "%_bld%" --config %_cfg%
if errorlevel 1 (
    echo [ERROR] CMake Build failed for %_cfg%/%_arc%
    exit /b 1
)
exit /b 0

:: -----------------------------------------------------------------------------
:: Helper: Copy Libraries
:: -----------------------------------------------------------------------------
:CopyLibs
set "_src_dir=%~1"
set "_in_arch=%~2"

:: Map Win32 -> x86 for output
set "_out_arch=%_in_arch%"
if /i "%_out_arch%"=="Win32" set "_out_arch=x86"

set "_dst_dir=../bin/curl/lib/%_out_arch%"

if not exist "%_dst_dir%" md "%_dst_dir%" >nul 2>&1
echo     Copying libs to %_dst_dir%...
:: No /S to prevent copying nested libs
xcopy /Y "%_src_dir%\lib\*.lib" "%_dst_dir%\" >nul 2>&1
xcopy /Y "%_src_dir%\*.lib" "%_dst_dir%\" >nul 2>&1
exit /b 0