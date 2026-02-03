@echo off
:: Base Configuration
:: Auto-detects Visual Studio, configures environment and colors.

setlocal EnableDelayedExpansion

:: --- 1. Find Visual Studio ---
call :FindVisualStudio
if not defined vs_dir (
    echo [ERROR] Visual Studio not found.
    exit /b 1
)

:: --- 2. Setup Standard Paths ---
set "vs_vcvar64=%vs_dir%\VC\Auxiliary\Build\vcvars64.bat"
set "vs_vcvar32=%vs_dir%\VC\Auxiliary\Build\vcvars32.bat"
set "vs_vcvarall=%vs_dir%\VC\Auxiliary\Build\vcvarsall.bat"
set "vs_devcmd=%vs_dir%\Common7\Tools\VsDevCmd.bat"
set "vs_msbuildcmd=%vs_dir%\Common7\Tools\VsMSBuildCmd.bat"

:: --- 3. Setup Colors ---
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "CLR_RESET=%ESC%[0m"
set "CLR_RED=%ESC%[91m"
set "CLR_GREEN=%ESC%[92m"
set "CLR_YELLOW=%ESC%[93m"
set "CLR_BLUE=%ESC%[94m"
set "CLR_MAGENTA=%ESC%[95m"
set "CLR_CYAN=%ESC%[96m"
set "CLR_WHITE=%ESC%[97m"

:: --- 4. Export to Caller ---
endlocal & (
    set "vs_dir=%vs_dir%"
    set "vs_vcvar64=%vs_vcvar64%"
    set "vs_vcvar32=%vs_vcvar32%"
    set "vs_vcvarall=%vs_vcvarall%"
    set "vs_devcmd=%vs_devcmd%"
    set "vs_msbuildcmd=%vs_msbuildcmd%"
    set "ESC=%ESC%"
    set "CLR_RESET=%CLR_RESET%"
    set "CLR_RED=%CLR_RED%"
    set "CLR_GREEN=%CLR_GREEN%"
    set "CLR_YELLOW=%CLR_YELLOW%"
    set "CLR_BLUE=%CLR_BLUE%"
    set "CLR_MAGENTA=%CLR_MAGENTA%"
    set "CLR_CYAN=%CLR_CYAN%"
    set "CLR_WHITE=%CLR_WHITE%"
)

call :setPath git ..\usr\bin
set "PATH=%~dp0;%PATH%"
goto :eof

:: -----------------------------------------------------------------------------
:: Helper Functions
:: -----------------------------------------------------------------------------

:FindVisualStudio
    set "vswhere=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
    if exist "%vswhere%" (
        for /f "usebackq tokens=*" %%i in (`"%vswhere%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
            if exist "%%i\Common7\Tools\VsDevCmd.bat" (
                set "vs_dir=%%i"
                exit /b 0
            )
        )
    )

    call :CheckVSPath "%PROGRAMFILES%\Microsoft Visual Studio\2022\Professional"
    if defined vs_dir exit /b 0

    call :CheckVSPath "%PROGRAMFILES%\Microsoft Visual Studio\18\Professional"
    if defined vs_dir exit /b 0
    
    set "root=%PROGRAMFILES%\Microsoft Visual Studio\2022"
    if exist "%root%" (
        for /d %%d in ("%root%\*") do (
            call :CheckVSPath "%%d"
            if defined vs_dir exit /b 0
        )
    )
    exit /b 1

:CheckVSPath
    if exist "%~1\Common7\Tools\VsDevCmd.bat" set "vs_dir=%~1"
    exit /b 0

:setPath
    setlocal
    set "cmdName=%1"
    set "relPath=%~2"
    for /f "delims=" %%i in ('where %cmdName% 2^>nul') do (
        set "baseDir=%%~dpi"
        goto :Found
    )
    endlocal
    exit /b 1

:Found
    set "fullPath=%baseDir%%relPath%"
    for %%A in ("%fullPath%") do set "final=%%~fA"
    set "final=%final%\"
    endlocal & set "PATH=%final%;%PATH%"
    exit /b 0