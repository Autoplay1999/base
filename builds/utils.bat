@echo off
call :%*
if errorlevel 1 exit /b 1
exit /b 0

:: --- Logging Functions ---

:LogInfo
    echo %CLR_CYAN%[INFO]%CLR_RESET% %~1
    exit /b 0

:LogSuccess
    echo %CLR_GREEN%[SUCCESS]%CLR_RESET% %~1
    exit /b 0

:LogWarning
    echo %CLR_YELLOW%[WARNING]%CLR_RESET% %~1
    exit /b 0

:LogError
    echo %CLR_RED%[ERROR]%CLR_RESET% %~1
    exit /b 0

:: --- Build Functions ---

:UpdateSubmodule
    set "_module_path=%~1"
    git submodule update --init --recursive --force "%_module_path%" >nul 2>&1
    if errorlevel 1 (
        call :LogError "Failed to update submodule: %_module_path%"
        exit /b 1
    )
    exit /b 0

:PrepareDest
    set "_dest_path=%~1"
    set "_dest_path=%_dest_path:/=\%"
    if exist "%_dest_path%" rd /S /Q "%_dest_path%"
    md "%_dest_path%" >nul 2>&1
    exit /b 0

:CopyHeaders
    set "_src=%~1"
    set "_dst=%~2"
    set "_pat=%~3"
    set "_src=%_src:/=\%"
    set "_dst=%_dst:/=\%"
    if "%_pat%"=="" set "_pat=*.*"
    if not exist "%_dst%" md "%_dst%" >nul 2>&1
    xcopy /S /E /H /Y /R "%_src%\%_pat%" "%_dst%\" >nul 2>&1
    exit /b 0

:CopyRecursive
    set "_src=%~1"
    set "_dst=%~2"
    set "_src=%_src:/=\%"
    set "_dst=%_dst:/=\%"
    xcopy /S /H /Y /R /I "%_src%" "%_dst%\" >nul 2>&1
    exit /b 0

:MSBuild
    set "_proj=%~1"
    set "_conf=%~2"
    set "_plat=%~3"
    set "_extra=%~4"
    
    msbuild "%_proj%" -p:Configuration="%_conf%" -p:Platform="%_plat%" %_extra% -t:Clean;Rebuild -v:q /nodeReuse:false >nul 2>&1
    if errorlevel 1 (
        call :LogError "MSBuild failed for %_proj% [%_conf% - %_plat%]. Retrying with output..."
        msbuild "%_proj%" -p:Configuration="%_conf%" -p:Platform="%_plat%" %_extra% -t:Clean;Rebuild /nodeReuse:false
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
    set "_sln=%~1"
    nuget restore "%_sln%" -MSBuildPath "%vs_dir%\MSBuild\Current\bin" >nul 2>&1
    if errorlevel 1 (
        call :LogError "NuGet restore failed for %_sln%"
        exit /b 1
    )
    exit /b 0
