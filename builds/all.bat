@echo off
setlocal EnableDelayedExpansion

for /F %%a in ('echo prompt $E ^| cmd') do (
    set "ESC=%%a"
)

set "_modules=curl imgui json lazy_importer neargye.magic_enum neargye.nameof neargye.semver neargye.yacppl neargye.scope_guard nirvana phnt tinycc turbo_base64 vmp xorstr xorstr2 zlib zydis knsoft.ndk knsoft.slimdetours knsoft.syscall asmjit simdjson yaml-cpp"

for %%i in (%_modules%) do (
    echo Building %ESC%[33m%%i%ESC%[0m%ESC%[37m...
    call %%i
    if errorlevel 1 (
        echo %ESC%[31mError%ESC%[0m%ESC%[37m: Failed to build %ESC%[33m%%i%ESC%[0m%ESC%[37m
    ) else (
        echo %ESC%[32mSuccessfully%ESC%[0m%ESC%[37m build %ESC%[33m%%i%ESC%[0m%ESC%[37m
    )
    echo.
)

echo All builds %ESC%[32mcompleted%ESC%[0m%ESC%[37m.