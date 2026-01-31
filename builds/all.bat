@echo off
setlocal EnableDelayedExpansion

call base

:: --- Configuration ---
set "_logs=..\logs"
if not exist "%_logs%" md "%_logs%" >nul 2>&1

set "_modules=curl imgui json lazy_importer neargye.magic_enum neargye.nameof neargye.semver neargye.yacppl neargye.scope_guard nirvana phnt tinycc turbo_base64 vmp xorstr obfuscate obfuscxx obfusheader.h zlib zydis knsoft.ndk knsoft.slimdetours knsoft.syscall asmjit simdjson yaml-cpp"

:: --- Start ---
echo [INFO] Starting Build Process...
echo [INFO] Visual Studio: %vs_dir%
echo [INFO] Logs Directory: %_logs%
echo.

set "success_count=0"
set "fail_count=0"

for %%i in (%_modules%) do (
    <nul set /p "=[%%i] Building... "
    
    call %%i > "%_logs%\%%i.log" 2>&1
    
    if errorlevel 1 (
        echo [FAILED]
        echo        See logs\%%i.log for details.
        set /a fail_count+=1
    ) else (
        echo [OK]
        set /a success_count+=1
    )
)

echo.
echo ==============================================
echo  Build Summary
echo ==============================================
echo  Successful: %success_count%
echo  Failed:     %fail_count%
echo ==============================================

if %fail_count% gtr 0 exit /b 1
exit /b 0
