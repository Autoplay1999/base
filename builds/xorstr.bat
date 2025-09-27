@echo off
setlocal EnableDelayedExpansion

set "_project=xorstr"
set "_dest=..\bin\!_project!"
set "_base=..\modules\!_project!"

if exist !_dest! rd /S /Q "!_dest!"
if exist !_base! rd /S /Q "!_base!"
git submodule update --init !_base! >nul 2>&1

md "!_dest!\include" >nul 2>&1
xcopy /H /Y /R "!_base!\include\*.hpp" "!_dest!\include\" >nul 2>&1
sed -i -e "/#define JM_XORSTR_HPP/a #define JM_XORSTR_DISABLE_AVX_INTRINSICS" -e "/#include <type_traits>/a\ \n#ifndef XS\n#    define _XSW(x) (PCWCH)XS(L##x)\n#    define _XS8(x) (PCCH)XS(u8##x)\n#    define XS(x) xorstr_(x)\n#    define XSA(x) (PCCH)XS(x)\n#    define XSW(x) _XSW(x)\n#    define XS8(x) _XS8(x)\n#endif" "!_dest!\include\xorstr.hpp"