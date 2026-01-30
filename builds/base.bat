@echo off
set "vs_dir=%PROGRAMFILES%\Microsoft Visual Studio\18\Professional"
set "vs_vcvar64=%vs_dir%\VC\Auxiliary\Build\vcvars64.bat"
set "vs_vcvar32=%vs_dir%\VC\Auxiliary\Build\vcvars32.bat"
set "vs_vcvarall=%vs_dir%\VC\Auxiliary\Build\vcvarsall.bat"
set "vs_devcmd=%vs_dir%\Common7\Tools\VsDevCmd.bat"
set "vs_msbuildcmd=%vs_dir%\Common7\Tools\VsMSBuildCmd.bat"

call :setPath git ..\usr\bin
goto :eof


:setPath
setlocal enabledelayedexpansion
set "cmdName=%1"
set "relPath=%~2"

for /f "delims=" %%i in ('where %cmdName% 2^>nul') do (
    set "baseDir=%%~dpi"
    
    for %%A in ("!baseDir!!relPath!") do set "final=%%~fA"
    
    if not "!final:~-1!"=="\" set "final=!final!\"
    
    for /f "delims=" %%p in ("!final!") do (
		endlocal
		set "PATH=%%p;%PATH%"
	)

    exit /b 0
)

endlocal
echo [error] Not Found %1
exit /b 1