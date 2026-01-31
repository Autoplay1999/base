@echo off
call :%*
exit /b

:UpdateSubmodule
    :: Usage: call utils.bat UpdateSubmodule "path/to/module"
    set "_module_path=%~1"
    if exist "%_module_path%" rd /S /Q "%_module_path%"
    git submodule update --init --recursive "%_module_path%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to update submodule: %_module_path%
        exit /b 1
    )
    exit /b 0

:CleanDest
    :: Usage: call utils.bat CleanDest "path/to/dest"
    set "_dest_path=%~1"
    if exist "%_dest_path%" rd /S /Q "%_dest_path%"
    exit /b 0

:PrepareDest
    :: Usage: call utils.bat PrepareDest "path/to/dest"
    set "_dest_path=%~1"
    if exist "%_dest_path%" rd /S /Q "%_dest_path%"
    md "%_dest_path%" >nul 2>&1
    exit /b 0

:CopyHeaders
    :: Usage: call utils.bat CopyHeaders "source_dir" "dest_dir" "pattern"
    set "_src=%~1"
    set "_dst=%~2"
    set "_pat=%~3"
    if "%_pat%"=="" set "_pat=*.*"
    
    if not exist "%_dst%" md "%_dst%" >nul 2>&1
    xcopy /H /Y /R "%_src%\%_pat%" "%_dst%\" >nul 2>&1
    exit /b 0

:CopyRecursive
    :: Usage: call utils.bat CopyRecursive "source_dir" "dest_dir"
    set "_src=%~1"
    set "_dst=%~2"
    
    xcopy /S /H /Y /R /I "%_src%" "%_dst%\" >nul 2>&1
    exit /b 0
