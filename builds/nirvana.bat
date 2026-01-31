@echo off
setlocal EnableDelayedExpansion
call base
call utils UpdateSubmodule "../modules/nirvana"
call utils PrepareDest "../bin/nirvana/include"
call utils CopyHeaders "../modules/nirvana/include" "../bin/nirvana/include"