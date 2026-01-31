@echo off
setlocal EnableDelayedExpansion
call base

set "_project_path=imgui"
set "_dirs=master docking win98"
set "_vcs=imgui imgui_dx9 imgui_dx11 imgui_win32"

call "!vs_msbuildcmd!" >nul 2>&1

for %%D in (%_dirs%) do (
    set "_dest=../bin/imgui/%%D"
    set "_base=../modules/imgui/%%D/imgui"
    
    call utils UpdateSubmodule "!_base!"
    call utils PrepareDest "!_dest!"
    
    md "!_dest!/lib" "!_dest!/include" >nul 2>&1
    call utils CopyHeaders "!_base!" "!_dest!/include" "*.h"

    for %%V in (%_vcs%) do (
        set "_vcxproj=imgui/%%D/%%V.vcxproj"
        if exist "!_vcxproj!" (
            call utils MSBuildAll "!_vcxproj!" || exit /b 1
        )
    )
    
    if exist "imgui/%%D/bin/lib" (
        call utils CopyRecursive "imgui/%%D/bin/lib" "!_dest!/lib"
        rd /S /Q "imgui/%%D/bin" >nul 2>&1
    )
)
