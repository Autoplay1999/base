@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/scope_guard"
call utils PrepareDest "../bin/neargye/include/neargye/scope_guard"
call utils CopyRecursive "../modules/scope_guard/include/scope_guard" "../bin/neargye/include/neargye/scope_guard"