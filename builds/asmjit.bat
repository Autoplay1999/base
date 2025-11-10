@echo off
setlocal EnableDelayedExpansion

set "_project=asmjit"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"
set "_output=!_base!\build"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init --recursive !_base! >nul 2>&1

call base

pushd "!_base!"
call "!vs_vcvarall!" x86 >nul 2>&1
cmake . -B build/x86/release -G"Visual Studio 17 2022" -A Win32 -DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded >nul 2>&1
pushd "build/x86/release"
cmake --build . --config Release --target asmjit -- -m >nul 2>&1
popd
cmake . -B build/x86/debug -G"Visual Studio 17 2022" -A Win32 -DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDebug >nul 2>&1
pushd "build/x86/debug"
cmake --build . --config Debug --target asmjit -- -m >nul 2>&1
popd

call "!vs_vcvarall!" x64 >nul 2>&1

cmake . -B build/x64/release -G"Visual Studio 17 2022" -A x64 -DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded >nul 2>&1
pushd "build/x64/release"
cmake --build . --config Release --target asmjit -- -m >nul 2>&1
popd
cmake . -B build/x64/debug -G"Visual Studio 17 2022" -A x64 -DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDebug >nul 2>&1
pushd "build/x64/debug"
cmake --build . --config Debug --target asmjit -- -m >nul 2>&1
popd
popd

md "!_dest!\lib\x86\debug" "!_dest!\lib\x64\debug" "!_dest!\lib\x86\release" "!_dest!\lib\x64\release" "!_dest!\include\!_project!" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\x86\debug\Debug" "!_dest!\lib\x86\debug" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\x64\debug\Debug" "!_dest!\lib\x64\debug" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\x86\release\Release" "!_dest!\lib\x86\release" >nul 2>&1
xcopy /S /H /Y /R /I "!_output!\x64\release\Release" "!_dest!\lib\x64\release" >nul 2>&1
xcopy /S /H /Y /R /I "!_base!\!_project!\*.h" "!_dest!\include\!_project!" >nul 2>&1