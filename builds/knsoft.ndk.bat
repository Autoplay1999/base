@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\KNSoft.NDK"
call utils PrepareDest "..\bin\KNSoft"

set "_base=..\modules\KNSoft.NDK"
set "_sln=!_base!\Source\KNSoft.NDK.sln"

call utils NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
:: Build manually because KNSoft uses 'x86' instead of 'Win32'
call utils MSBuild "!_sln!" "Release" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Release" "x86" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x86" || exit /b 1

set "_out=!_base!\Source\OutDir"
call utils PrepareDest "..\bin\KNSoft\lib\x86\release"
call utils CopyRecursive "!_out!\x86" "..\bin\KNSoft\lib\x86\release"
call utils PrepareDest "..\bin\KNSoft\lib\x64\release"
call utils CopyRecursive "!_out!\x64" "..\bin\KNSoft\lib\x64\release"
call utils PrepareDest "..\bin\KNSoft\lib\x86\debug"
call utils CopyRecursive "!_out!\x86" "..\bin\KNSoft\lib\x86\debug"
call utils PrepareDest "..\bin\KNSoft\lib\x64\debug"
call utils CopyRecursive "!_out!\x64" "..\bin\KNSoft\lib\x64\debug"

call utils CopyRecursive "!_base!\Source\Include" "..\bin\KNSoft\include"
