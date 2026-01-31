@echo off
setlocal EnableDelayedExpansion

call :FindVisualStudio
if not defined vs_dir (
    echo [ERROR] Visual Studio not found.
    exit /b 1
)

:: Export
endlocal & (
    set "vs_dir=%vs_dir%"
    set "vs_vcvar64=%vs_dir%\VC\Auxiliary\Build\vcvars64.bat"
    set "vs_vcvar32=%vs_dir%\VC\Auxiliary\Build\vcvars32.bat"
    set "vs_vcvarall=%vs_dir%\VC\Auxiliary\Build\vcvarsall.bat"
    set "vs_devcmd=%vs_dir%\Common7\Tools\VsDevCmd.bat"
    set "vs_msbuildcmd=%vs_dir%\Common7\Tools\VsMSBuildCmd.bat"
)
call :setPath git ..\usr\bin
goto :eof

:FindVisualStudio
    :: VSWHERE check removed for safety for now, relying on fallback
    
    call :CheckVSPath "%PROGRAMFILES%\Microsoft Visual Studio\2022\Professional"
    if defined vs_dir exit /b 0

    call :CheckVSPath "%PROGRAMFILES%\Microsoft Visual Studio\18\Professional"
    if defined vs_dir exit /b 0
    
    :: Try finding any VS 2022
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