@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\obfuscxx"
call utils PrepareDest "..\bin\obfuscxx\include"
call utils CopyHeaders "..\modules\obfuscxx\obfuscxx\include" "..\bin\obfuscxx\include" "obfuscxx.h"