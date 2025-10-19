@echo off
setlocal EnableDelayedExpansion

set "_project=curl"
set "_output=!_project!\bin"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"
set "_build=!_dest!\_!_project!"

set RTLIBCFG=static
set WINBUILD_ACKNOWLEDGE_DEPRECATED=yes

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init !_base!  >nul 2>&1
pushd !_base!
git checkout curl-8_16_0
popd

call base
md "!_dest!\lib" "!_dest!\include" 2>nul
xcopy /S /H /Y /R /I "!_base!" "!_build!" >nul 2>&1
pushd "!_build!\winbuild"
call "!vs_vcvar64!" >nul 2>&1
nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=yes GEN_PDB=yes MACHINE=x64 >nul 2>&1
if %ERRORLEVEL% neq 0 goto :eof
nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=no GEN_PDB=no MACHINE=x64 >nul 2>&1
if %ERRORLEVEL% neq 0 goto :eof
call "!vs_vcvar32!" >nul 2>&1
nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=yes GEN_PDB=yes MACHINE=x86 >nul 2>&1
if %ERRORLEVEL% neq 0 goto :eof
nmake /f Makefile.vc RTLIBCFG=static mode=static DEBUG=no GEN_PDB=no MACHINE=x86 >nul 2>&1
if %ERRORLEVEL% neq 0 goto :eof
popd
pushd "!_build!\builds"
xcopy /S /H /Y /R /I  "libcurl-vc-x64-debug-static-ipv6-sspi-schannel\lib" "..\..\lib\x64\" >nul 2>&1
xcopy /S /H /Y /R /I  "libcurl-vc-x64-release-static-ipv6-sspi-schannel\lib" "..\..\lib\x64\" >nul 2>&1
xcopy /S /H /Y /R /I  "libcurl-vc-x86-debug-static-ipv6-sspi-schannel\lib" "..\..\lib\x86\" >nul 2>&1
xcopy /S /H /Y /R /I  "libcurl-vc-x86-release-static-ipv6-sspi-schannel\lib" "..\..\lib\x86\" >nul 2>&1
xcopy /H /Y /R  "..\include\curl\*.h" "..\..\include\" >nul 2>&1
popd
rd /S /Q "!_build!" >nul 2>&1