@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/yacppl"
call utils PrepareDest "../bin/neargye/include/neargye/yacppl"
call utils CopyHeaders "../modules/yacppl/include" "../bin/neargye/include/neargye/yacppl"
