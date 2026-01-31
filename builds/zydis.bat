@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/zydis"
call utils PrepareDest "../bin/zydis"

set "_sln=../modules/zydis/msvc/zydis.sln"
set "_targets=-t:Zycore:Clean;Zycore:Rebuild;Zydis:Clean;Zydis:Rebuild"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuild "!_sln!" "Release MT" "x64" "!_targets!" || exit /b 1
call utils MSBuild "!_sln!" "Debug MT" "x64" "!_targets!" || exit /b 1
call utils MSBuild "!_sln!" "Release MT" "x86" "!_targets!" || exit /b 1
call utils MSBuild "!_sln!" "Debug MT" "x86" "!_targets!" || exit /b 1

set "_out=../modules/zydis/msvc/bin"
call utils CopyRecursive "!_out!/ReleaseX64" "../bin/zydis/lib/x64/release"
call utils CopyRecursive "!_out!/DebugX64" "../bin/zydis/lib/x64/debug"
call utils CopyRecursive "!_out!/ReleaseX86" "../bin/zydis/lib/x86/release"
call utils CopyRecursive "!_out!/DebugX86" "../bin/zydis/lib/x86/debug"

call utils CopyRecursive "../modules/zydis/include" "../bin/zydis/include"
call utils CopyRecursive "../modules/zydis/dependencies/zycore/include" "../bin/zydis/include"
