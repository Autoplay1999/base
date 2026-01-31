@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/nameof"
call utils PrepareDest "../bin/neargye/include/neargye/nameof"
call utils CopyRecursive "../modules/nameof/include/nameof" "../bin/neargye/include/neargye/nameof"