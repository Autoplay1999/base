@echo off
setlocal EnableDelayedExpansion

set "_project_path=imgui"
set "_project_dir=master docking win98"
set "_project=imgui imgui_dx9 imgui_dx11 imgui_win32"
set "_configurations=Release Debug"
set "_platforms=x64 Win32"

call base
call "!vs_msbuildcmd!" >nul 2>&1

for %%D in (!_project_dir!) do (
	set "_output=!_project_path!\%%D\bin"
	set "_dest=..\bin\!_project_path!\%%D"
	set "_base=..\modules\!_project_path!\%%D\!_project_path!"

	if exist "!_dest!" rd /S /Q "!_dest!" >nul 2>&1
	if exist "!_base!" rd /S /Q "!_base!" >nul 2>&1
	git submodule update --init --recursive "!_base!" >nul 2>&1
	
	md "!_dest!\lib" "!_dest!\include" >nul 2>&1
	xcopy /S /H /Y /R /I "!_base!\*.h" "!_dest!\include\" >nul 2>&1

    for %%P in (!_project!) do (
        for %%C in (!_configurations!) do (
            for %%A in (!_platforms!) do (
                msbuild "!_project_path!\%%D\%%P.vcxproj" -p:Configuration=%%C -p:Platform=%%A -t:Clean;Rebuild -v:q >nul 2>&1
                if !ERRORLEVEL! neq 0 (
                    echo Build failed for %%P, %%D, Configuration=%%C, Platform=%%A
                    goto :EOF
                )
            )
        )

        xcopy /S /H /Y /R /I "!_output!\lib" "!_dest!\lib\" >nul 2>&1
        rd /S /Q "!_output!" >nul 2>&1
    )
)

:end
endlocal