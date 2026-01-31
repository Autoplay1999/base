@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "..\modules\obfusheader.h"
call utils PrepareDest "..\bin\obfusheader.h\include"
call utils CopyHeaders "..\modules\obfusheader.h\include" "..\bin\obfusheader.h\include" "obfusheader.h"