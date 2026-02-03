@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0base"

set "_bin=%~dp0..\bin\imgui"
if exist "!_bin!" rd /S /Q "!_bin!"

:: 1. Global Update Submodules
echo [INFO] Updating ImGui Submodules...
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\imgui\master\imgui"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\imgui\docking\imgui"
call "%~dp0utils" UpdateSubmodule "%~dp0..\modules\imgui\win98\imgui"

set "_dirs=master docking win98"
set "_vcs=imgui imgui_stdlib imgui_dx9 imgui_dx11 imgui_win32"

call "!vs_msbuildcmd!" >nul 2>&1

for %%D in (%_dirs%) do (
    echo [INFO] Building ImGui %%D...
    set "_variant_bin=!_bin!\%%D"
    set "_module_src=%~dp0..\modules\imgui\%%D\imgui"
    set "_build_root=%~dp0imgui\%%D"
    
    call "%~dp0utils" PrepareDest "!_variant_bin!"
    md "!_variant_bin!\lib" "!_variant_bin!\include" >nul 2>&1
    
    :: Precise Header Collection
    echo [INFO] Collecting headers for %%D...
    :: Root headers
    copy /y "!_module_src!\*.h" "!_variant_bin!\include\" >nul 2>&1
    
    :: Backends headers
    md "!_variant_bin!\include\backends" >nul 2>&1
    copy /y "!_module_src!\backends\*.h" "!_variant_bin!\include\backends\" >nul 2>&1
    
    :: Misc headers (keeping structure for cpp, freetype etc)
    call "%~dp0utils" CopyHeaders "!_module_src!\misc" "!_variant_bin!\include\misc" "*.h"
    
    :: Fonts (Copy directly to include/misc/fonts or include/fonts? ImGui usually uses them from misc/fonts)
    :: But the user might want them available. Let's include the fonts dir under misc.
    call "%~dp0utils" CopyRecursive "!_module_src!\misc\fonts" "!_variant_bin!\include\misc\fonts"

    for %%V in (%_vcs%) do (
        set "_vcxproj=!_build_root!\%%V.vcxproj"
        if exist "!_vcxproj!" (
            echo [INFO] Building %%D/%%V...
            msbuild "!_vcxproj!" -p:Configuration=Release -p:Platform=x64 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Debug -p:Platform=x64 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Release -p:Platform=Win32 -m /nodeReuse:false -v:q >nul 2>&1
            msbuild "!_vcxproj!" -p:Configuration=Debug -p:Platform=Win32 -m /nodeReuse:false -v:q >nul 2>&1
        )
    )
    
    :: Precise Library Collection
    if exist "!_build_root!\bin\lib" (
        echo [INFO] Organizing libraries for %%D...
        for %%a in (x64 x86) do (
            for %%c in (release debug) do (
                set "_src=!_build_root!\bin\lib\%%a\%%c"
                set "_dst=!_variant_bin!\lib\%%a\%%c"
                if not exist "!_dst!" md "!_dst!" >nul 2>&1
                if exist "!_src!" (
                    copy /y "!_src!\*.lib" "!_dst!\" >nul 2>&1
                )
            )
        )
        rd /S /Q "!_build_root!\bin" >nul 2>&1
    )
)

echo [SUCCESS] ImGui build completed successfully.
