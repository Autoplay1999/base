@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/KNSoft.Syscall"
call utils NuGetRestore "../modules/KNSoft.Syscall/Source/KNSoft.Syscall.sln"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuildAll "../modules/KNSoft.Syscall/Source/KNSoft.Syscall.sln" || exit /b 1

set "_out=../modules/KNSoft.Syscall/Source/OutDir"
call utils CopyRecursive "!_out!/x86/Release" "../bin/KNSoft/lib/x86/release"
call utils CopyRecursive "!_out!/x64/Release" "../bin/KNSoft/lib/x64/release"
call utils CopyRecursive "!_out!/x86/Debug" "../bin/KNSoft/lib/x86/debug"
call utils CopyRecursive "!_out!/x64/Debug" "../bin/KNSoft/lib/x64/debug"

call utils PrepareDest "../bin/KNSoft/include/KNSoft/Syscall"
call utils CopyHeaders "../modules/KNSoft.Syscall/Source/KNSoft.Syscall" "../bin/KNSoft/include/KNSoft/Syscall" "Syscall.h"
call utils CopyHeaders "../modules/KNSoft.Syscall/Source/KNSoft.Syscall" "../bin/KNSoft/include/KNSoft/Syscall" "Syscall.Thunks.h"
