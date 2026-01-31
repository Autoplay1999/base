@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/asmjit"
call utils PrepareDest "../bin/asmjit"

:: Activate VS Environment (for CMake, etc.)
call "!vs_devcmd!" -no_logo >nul 2>&1

set "_base=../modules/asmjit"
set "_build=!_base!/build"
set "_cmake_args=-DASMJIT_TEST=OFF -DASMJIT_STATIC=ON -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded"

:: x86
call utils CMakeBuild "!_base!" "!_build!/x86/release" "Win32" "Release" "!_cmake_args!" || exit /b 1
call utils CMakeBuild "!_base!" "!_build!/x86/debug" "Win32" "Debug" "!_cmake_args!Debug" || exit /b 1

:: x64
call utils CMakeBuild "!_base!" "!_build!/x64/release" "x64" "Release" "!_cmake_args!" || exit /b 1
call utils CMakeBuild "!_base!" "!_build!/x64/debug" "x64" "Debug" "!_cmake_args!Debug" || exit /b 1

:: Copy Outputs
call utils PrepareDest "../bin/asmjit/lib/x86/release"
call utils CopyRecursive "!_build!/x86/release/Release" "../bin/asmjit/lib/x86/release"
call utils PrepareDest "../bin/asmjit/lib/x86/debug"
call utils CopyRecursive "!_build!/x86/debug/Debug" "../bin/asmjit/lib/x86/debug"
call utils PrepareDest "../bin/asmjit/lib/x64/release"
call utils CopyRecursive "!_build!/x64/release/Release" "../bin/asmjit/lib/x64/release"
call utils PrepareDest "../bin/asmjit/lib/x64/debug"
call utils CopyRecursive "!_build!/x64/debug/Debug" "../bin/asmjit/lib/x64/debug"

call utils CopyRecursive "!_base!/src/asmjit" "../bin/asmjit/include/asmjit"