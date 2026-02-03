@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/vmp"
call utils PrepareDest "../bin/vmp"

call utils CopyHeaders "../modules/vmp/include" "../bin/vmp/include" "*.h"
call utils CopyRecursive "../modules/vmp/lib" "../bin/vmp/lib"
call utils CopyRecursive "../modules/vmp/bin" "../bin/vmp/bin"
