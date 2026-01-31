@echo off
setlocal EnableDelayedExpansion

call base

:: --- Configuration ---
set "_logs=..\logs"
if not exist "%_logs%" md "%_logs%" >nul 2>&1

set "_modules=curl imgui json lazy_importer neargye.magic_enum neargye.nameof neargye.semver neargye.yacppl neargye.scope_guard nirvana phnt tinycc turbo_base64 vmp xorstr obfuscate obfuscxx obfusheader.h zlib zydis knsoft.ndk knsoft.slimdetours knsoft.syscall asmjit simdjson yaml-cpp"

:: --- Start ---
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_WHITE%  BUILD SYSTEM%CLR_RESET%
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_WHITE%  Visual Studio : %vs_dir%%CLR_RESET%
echo %CLR_WHITE%  Logs Directory: %_logs%%CLR_RESET%
echo %CLR_CYAN%--------------------------------------------------------------%CLR_RESET%
echo.

set "success_count=0"
set "fail_count=0"

for %%i in (%_modules%) do (
    <nul set /p "=%CLR_WHITE%[%%i]%CLR_RESET% Building... "
    
    call %%i > "%_logs%\%%i.log" 2>&1
    
    if errorlevel 1 (
        echo %CLR_RED%[FAILED]%CLR_RESET%
        echo        %CLR_YELLOW%See logs\%%i.log for details.%CLR_RESET%
        set /a fail_count+=1
    ) else (
        echo %CLR_GREEN%[OK]%CLR_RESET%
        set /a success_count+=1
    )
)

echo.
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_WHITE%  BUILD SUMMARY%CLR_RESET%
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_GREEN%  Successful : %success_count%%CLR_RESET%
if %fail_count% gtr 0 (
    echo %CLR_RED%  Failed     : %fail_count%%CLR_RESET%
) else (
    echo %CLR_WHITE%  Failed     : %fail_count%%CLR_RESET%
)
echo %CLR_CYAN%==============================================================%CLR_RESET%

if %fail_count% gtr 0 exit /b 1
exit /b 0