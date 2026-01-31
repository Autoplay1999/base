@echo off
setlocal EnableDelayedExpansion
call base

echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_WHITE%  CLEAN SYSTEM%CLR_RESET%
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo.

:: 1. Global Directories
set "_to_clean=..\bin ..\logs"

:: 2. Project-specific temp directories
set "_modules=curl imgui json lazy_importer neargye.magic_enum neargye.nameof neargye.semver neargye.yacppl neargye.scope_guard nirvana phnt tinycc turbo_base64 vmp xorstr obfuscate obfuscxx obfusheader.h zlib zydis knsoft.ndk knsoft.slimdetours knsoft.syscall asmjit simdjson yaml-cpp"

for %%i in (%_modules%) do (
    set "_to_clean=!_to_clean! %%i\bin %%i\obj %%i\tmp %%i\OutDir"
)

set "_to_clean=!_to_clean! imgui\master\bin imgui\docking\bin imgui\win98\bin"

set "count=0"
for %%d in (%_to_clean%) do (
    if exist "%%d" (
        <nul set /p "=%CLR_WHITE%Cleaning %%d... %CLR_RESET%"
        rd /S /Q "%%d" >nul 2>&1
        if errorlevel 1 (
            echo %CLR_YELLOW%[LOCKED]%CLR_RESET%
        ) else (
            echo %CLR_GREEN%[DONE]%CLR_RESET%
            set /a count+=1
        )
    )
)

del /S /Q ..\sed* >nul 2>&1

echo.

echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_WHITE%  CLEAN SUMMARY%CLR_RESET%
echo %CLR_CYAN%==============================================================%CLR_RESET%
echo %CLR_GREEN%  Directories Removed : %count%%CLR_RESET%
echo %CLR_WHITE%  Status              : CLEANED%CLR_RESET%
echo %CLR_CYAN%==============================================================%CLR_RESET%
exit /b 0