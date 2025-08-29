@echo off
setlocal EnableDelayedExpansion

set "_modules=json lazy_importer magic_enum nameof nirvana phnt scope_guard semver tinycc turbo_base64 vmp xorstr yacppl zlib"

for %%i in (%_modules%) do (
    echo Building %%i...
    call %%i
    if errorlevel 1 (
        echo Error: Failed to build %%i
    ) else (
        echo Successfully build %%i
    )
    echo.
)

echo All builds completed.