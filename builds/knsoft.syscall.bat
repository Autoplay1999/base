@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\KNSoft.Syscall"
set "_sln=..\modules\KNSoft.Syscall\Source\KNSoft.Syscall.sln"

call utils NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuild "!_sln!" "Release" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Release" "x86" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x86" || exit /b 1

set "_out=..\modules\KNSoft.Syscall\Source\OutDir"
call utils CopyRecursive "!_out!\x86\Release" "..\bin\KNSoft\lib\x86\release"
call utils CopyRecursive "!_out!\x64\Release" "..\bin\KNSoft\lib\x64\release"
call utils CopyRecursive "!_out!\x86\Debug" "..\bin\KNSoft\lib\x86\debug"
call utils CopyRecursive "!_out!\x64\Debug" "..\bin\KNSoft\lib\x64\debug"

call utils PrepareDest "..\bin\KNSoft\include\KNSoft\Syscall"
call utils CopyHeaders "..\modules\KNSoft.Syscall\Source\KNSoft.Syscall" "..\bin\KNSoft\include\KNSoft\Syscall" "Syscall.h"
call utils CopyHeaders "..\modules\KNSoft.Syscall\Source\KNSoft.Syscall" "..\bin\KNSoft\include\KNSoft\Syscall" "Syscall.Thunks.h"
