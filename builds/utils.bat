@echo off
call :%*
exit /b

:UpdateSubmodule
    set "_module_path=%~1"
    if exist "%_module_path%" rd /S /Q "%_module_path%"
    git submodule update --init --recursive "%_module_path%" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to update submodule: %_module_path%
        exit /b 1
    )
    exit /b 0

:PrepareDest
    set "_dest_path=%~1"
    if exist "%_dest_path%" rd /S /Q "%_dest_path%"
    md "%_dest_path%" >nul 2>&1
    exit /b 0

:CopyHeaders
    set "_src=%~1"
    set "_dst=%~2"
    set "_pat=%~3"
    if "%_pat%"=="" set "_pat=*.*"
    if not exist "%_dst%" md "%_dst%" >nul 2>&1
    xcopy /H /Y /R "%_src%/%_pat%" "%_dst%/" >nul 2>&1
    exit /b 0

:CopyRecursive
    set "_src=%~1"
    set "_dst=%~2"
    xcopy /S /H /Y /R /I "%_src%" "%_dst%/" >nul 2>&1
    exit /b 0

:MSBuild
    set "_proj=%~1"
    set "_conf=%~2"
    set "_plat=%~3"
    set "_extra=%~4"
    msbuild "%_proj%" -p:Configuration="%_conf%" -p:Platform="%_plat%" %_extra% -t:Clean;Rebuild -v:q >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] MSBuild failed for %_proj% (%_conf%|%_plat%)
        exit /b 1
    )
    exit /b 0

:MSBuildAll
    set "_proj=%~1"
    call :MSBuild "%_proj%" "Release" "x64" || exit /b 1
    call :MSBuild "%_proj%" "Debug" "x64" || exit /b 1
    call :MSBuild "%_proj%" "Release" "Win32" || exit /b 1
    call :MSBuild "%_proj%" "Debug" "Win32" || exit /b 1
    exit /b 0

:CMakeBuild
    set "_src=%~1"
    set "_build=%~2"
    set "_arch=%~3"
    set "_conf=%~4"
    set "_args=%~5"
    cmake "%_src%" -B "%_build%" -G"Visual Studio 17 2022" -A "%_arch%" %_args% >nul 2>&1 || exit /b 1
    cmake --build "%_build%" --config "%_conf%" -- -m >nul 2>&1 || exit /b 1
    exit /b 0

:NuGetRestore
    :: Usage: call utils NuGetRestore "solution.sln"
    set "_sln=%~1"
    nuget restore "%_sln%" -MSBuildPath "%vs_dir%\MSBuild\Current\bin" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] NuGet restore failed for %_sln%
        exit /b 1
    )
    exit /b 0