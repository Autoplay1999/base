@echo off
set "vs_dir=%PROGRAMFILES%\Microsoft Visual Studio\2022\Professional"
set "vs_vcvar64=%vs_dir%\VC\Auxiliary\Build\vcvars64.bat"
set "vs_vcvar32=%vs_dir%\VC\Auxiliary\Build\vcvars32.bat"
set "vs_devcmd=%vs_dir%\Common7\Tools\VsDevCmd.bat"
set "vs_msbuildcmd=%vs_dir%\Common7\Tools\VsMSBuildCmd.bat"