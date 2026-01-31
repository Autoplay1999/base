@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\Obfuscate"
call utils PrepareDest "..\bin\Obfuscate\include"
call utils CopyHeaders "..\modules\Obfuscate" "..\bin\Obfuscate\include" "obfuscate.h"