@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/nameof"
call utils PrepareDest "../bin/neargye/include/neargye/nameof"
call utils CopyHeaders "../modules/nameof/include" "../bin/neargye/include/neargye/nameof"