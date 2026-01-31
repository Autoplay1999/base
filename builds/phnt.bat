@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/phnt"
call utils PrepareDest "../bin/phnt/include"
call utils CopyHeaders "../modules/phnt" "../bin/phnt/include" "*.h"