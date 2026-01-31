@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/xorstr"
call utils PrepareDest "../bin/xorstr/include"
call utils CopyHeaders "../modules/xorstr/include" "../bin/xorstr/include" "*.hpp"

:: Apply Patch
sed -i -e "/#define JM_XORSTR_HPP/a #define JM_XORSTR_DISABLE_AVX_INTRINSICS" -e "/#include <type_traits>/a\ \n#ifndef XS\n#    define _XSW(x) (PCWCH)XS(L##x)\n#    define _XS8(x) (PCCH)XS(u8##x)\n#    define XS(x) xorstr_(x)\n#    define XSA(x) (PCCH)XS(x)\n#    define XSW(x) _XSW(x)\n#    define XS8(x) _XS8(x)\n#endif" "../bin/xorstr/include/xorstr.hpp"