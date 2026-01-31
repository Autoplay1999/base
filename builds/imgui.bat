@echo off
setlocal EnableDelayedExpansion
call base

:: 1. Global Update Submodules (Run once for all imgui dirs)
echo [INFO] Updating ImGui Submodules...
pushd ..
    git submodule update --init --recursive --force modules/imgui/master/imgui >nul 2>&1
    git submodule update --init --recursive --force modules/imgui/docking/imgui >nul 2>&1
    git submodule update --init --recursive --force modules/imgui/win98/imgui >nul 2>&1
popd

set "_dirs=master docking win98"
set "_vcs=imgui imgui_dx9 imgui_dx11 imgui_win32"

call "!vs_msbuildcmd!" >nul 2>&1

for %%D in (%_dirs%) do (
    echo [INFO] Building ImGui %%D...
    set "_dest=../bin/imgui/%%D"
    set "_base=../modules/imgui/%%D/imgui"
    
    :: Just prepare destination, don't update submodule here
    call utils PrepareDest "!_dest!"
    md "!_dest!/lib" "!_dest!/include" >nul 2>&1
    call utils CopyHeaders "!_base!" "!_dest!/include" "*.h"

    for %%V in (%_vcs%) do (
        set "_vcxproj=imgui/%%D/%%V.vcxproj"
        if exist "!_vcxproj!" (
            :: Build using MSBuild directly with Multi-Processor flag for speed
            msbuild "!_vcxproj!" -p:Configuration=Release -p:Platform=x64 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Debug -p:Platform=x64 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Release -p:Platform=Win32 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Debug -p:Platform=Win32 -m /nodeReuse:false -v:q >nul 2>&1
        )
    )
    
    if exist "imgui/%%D/bin/lib" (
        call utils CopyRecursive "imgui/%%D/bin/lib" "!_dest!/lib"
        rd /S /Q "imgui/%%D/bin" >nul 2>&1
    )
)
