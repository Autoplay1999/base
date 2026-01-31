@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/yacppl"
call utils PrepareDest "../bin/neargye/include/neargye/yacppl"
call utils CopyRecursive "../modules/yacppl/include/yacppl" "../bin/neargye/include/neargye/yacppl"
