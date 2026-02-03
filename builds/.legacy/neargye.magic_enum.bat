@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/magic_enum"
call utils PrepareDest "../bin/neargye/include/neargye/magic_enum"
call utils CopyRecursive "../modules/magic_enum/include/magic_enum" "../bin/neargye/include/neargye/magic_enum"