@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/yaml-cpp"
call utils PrepareDest "../bin/yaml-cpp"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuildAll "yaml-cpp/yaml-cpp.vcxproj" || exit /b 1

call utils CopyRecursive "yaml-cpp/bin/lib" "../bin/yaml-cpp/lib"
call utils CopyRecursive "../modules/yaml-cpp/include" "../bin/yaml-cpp/include"

if exist "yaml-cpp/bin" rd /S /Q "yaml-cpp/bin"

echo [INFO] Patching dll.h...
set "_target=../bin/yaml-cpp/include/yaml-cpp/dll.h"
if exist "!_target!" (
    sed -i "/#define DLL_H_/a \#define YAML_CPP_STATIC_DEFINE" "!_target!"
)

