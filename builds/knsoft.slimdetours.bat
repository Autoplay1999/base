@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\KNSoft.SlimDetours"
set "_sln=..\modules\KNSoft.SlimDetours\Source\KNSoft.SlimDetours.sln"

call utils NuGetRestore "!_sln!"

call "!vs_msbuildcmd!" >nul 2>&1
call utils MSBuild "!_sln!" "Release" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x64" || exit /b 1
call utils MSBuild "!_sln!" "Release" "x86" || exit /b 1
call utils MSBuild "!_sln!" "Debug" "x86" || exit /b 1

set "_out=..\modules\KNSoft.SlimDetours\Source\OutDir"
call utils CopyRecursive "!_out!\x86\Release" "..\bin\KNSoft\lib\x86\release"
call utils CopyRecursive "!_out!\x64\Release" "..\bin\KNSoft\lib\x64\release"
call utils CopyRecursive "!_out!\x86\Debug" "..\bin\KNSoft\lib\x86\debug"
call utils CopyRecursive "!_out!\x64\Debug" "..\bin\KNSoft\lib\x64\debug"

call utils PrepareDest "..\bin\KNSoft\include\KNSoft\SlimDetours"
call utils CopyHeaders "..\modules\KNSoft.SlimDetours\Source\KNSoft.SlimDetours" "..\bin\KNSoft\include\KNSoft\SlimDetours" "SlimDetours.h"
call utils CopyHeaders "..\modules\KNSoft.SlimDetours\Source\KNSoft.SlimDetours" "..\bin\KNSoft\include\KNSoft\SlimDetours" "SlimDetours.inl"
call utils CopyHeaders "..\modules\KNSoft.SlimDetours\Source\KNSoft.SlimDetours" "..\bin\KNSoft\include\KNSoft\SlimDetours" "SlimDetours.NDK.inl"
