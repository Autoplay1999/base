@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/scope_guard"
call utils PrepareDest "../bin/neargye/include/neargye/scope_guard"
call utils CopyHeaders "../modules/scope_guard/include" "../bin/neargye/include/neargye/scope_guard"